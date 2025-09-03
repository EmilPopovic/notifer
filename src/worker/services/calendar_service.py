import time
import logging
import hashlib
import requests
from datetime import datetime

from shared.calendar_utils import is_valid_ical, compute_ical_changes
from shared.models import UserCalendar
from shared.database import SessionLocal
from shared.storage_manager import StorageManager
from shared.email_client import EmailClient

logger = logging.getLogger(__name__)

class CalendarService:
    '''Service for processing individual calendar subscriptions.'''

    def __init__(self, storage_manager: StorageManager, email_client: EmailClient, base_calendar_url: str):
        self.storage_manager = storage_manager
        self.email_client = email_client
        self.base_calendar_url = base_calendar_url

    def compute_hash(self, content: str) -> str:
        '''Compute SHA256 hash of calendar content.'''
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def fetch_calendar_with_retry(self, url: str, retries: int = 3, backoff_factor: float = 30) -> str | None:
        '''
        Fetch calendar content with retry logic.

        Args:
            url: Calendar URL to fetch
            retries: Number of retry attempts
            backoff_factor: Exponential backoff factor

        Returns:
            Calendar content as string, or None if failed
        '''
        for attempt in range(1, retries + 1):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return response.text
                else:
                    logger.warning(f'Non-200 status ccode {response.status_code} when fetching {url}')
            except Exception as e:
                logger.exception(f'Exception fetching {url}: {e}')

            if attempt < retries:  # Don't sleep on the last attempt
                sleep_time = backoff_factor * (2 ** (attempt - 1))
                logger.info(f'Retrying in {sleep_time} seconds.')
                time.sleep(sleep_time)

        return None
    
    def get_previous_calendar_content(self, subscription: UserCalendar) -> str | None:
        '''Get previous calendar content from S3.'''
        if not subscription.previous_calendar_path:
            return None
        
        previous_content = self.storage_manager.get_calendar(subscription.email)
        if previous_content is None:
            logger.warning(f'Previous calendar missing or failed from S3 for {subscription.email}')

        return previous_content
    
    def save_calendar_to_s3(self, email: str, content: str) -> str | None:
        '''Save calendar content to S3 and return the URL.'''
        calendar_s3_url = self.storage_manager.save_calendar(email, content)
        if not calendar_s3_url:
            logger.error(f'Failed to upload updated calendar for {email} to S3')
        return calendar_s3_url
    
    def detect_and_notify_changes(self, subscription: UserCalendar, previous_content: str | None, new_content: str | None) -> bool:
        '''
        Detect changes between calendars and send notifications if needed.

        Returns:
            True if changes were detected and email enqueued, False otherwise
        '''
        event_changes = compute_ical_changes(
            old_ical=previous_content or '',
            new_ical=new_content or ''
        )

        if event_changes:
            logger.info(f'Detected {len(event_changes)} event changes for {subscription.email}')
            # Get user's language preference for notifications
            language: str = getattr(subscription, 'language', 'hr')
            self.email_client.send_notification_email(subscription.email, event_changes, language)
            return True
        else:
            logger.info(f'Calendar content changed but no event differences found for {subscription.email}')
            return False
        
    def process_subscription(self, sub: UserCalendar) -> dict:
        '''
        Process a single subscription for calendar changes.

        Args:
            subscription: UserCalendar instance to process

        Returns:
            True if processing was successful, False otherwise
        '''
        session = SessionLocal()

        status = {
            'error': None,
            'email_queued': False,
            'skipped': False,
            'is_initial': False,
            'treated_as_initial': False,
            'no_changes': True
        }

        try:
            # Get fresh subscription object in current session
            subscription = session.query(UserCalendar).filter(
                UserCalendar.username == sub.username,
                UserCalendar.domain == sub.domain
            ).with_for_update().first()

            if not subscription:
                logger.error(f'Subscription not found: {sub.email}')
                return {'error': 'SUBSCRIPTION_NOT_FOUND'}

            # Skip if not activated or paused
            if not subscription.activated or subscription.paused:
                logger.info(f'Skipping {subscription.email} (not activated or paused)')
                status['skipped'] = True
                return status
            
            # Build calendar URL
            calendar_url = f'{self.base_calendar_url}?user={subscription.username}&auth={subscription.calendar_auth}'
            logger.info(f'Fetching calendar for {subscription.email} from {calendar_url}')

            # Fetch current calendar content
            current_content = self.fetch_calendar_with_retry(calendar_url)
            if current_content is None:
                logger.error(f'Failed to fetch calendar for {subscription.email} after retries')
                status['error'] = 'FAILED_FETCH'
                return status
            
            # Validate calendar content
            if not is_valid_ical(current_content):
                logger.error(f'Fetched calendar for {subscription.email} is not a valid iCal document')
                status['error'] = 'INVALID_ICAL'
                return status
            
            # Compute new hash
            new_hash = self.compute_hash(current_content)

            # Determine if this is initial processing
            is_initial = not subscription.previous_calendar_path
            status['is_initial'] = is_initial
            previous_content = None

            if not is_initial:
                previous_content = self.get_previous_calendar_content(subscription)
                # Treat as initial if previous calendar document missing in S3
                if previous_content is None:
                    logger.warning(f'Treating {subscription.email} as initial due to missing previous calendar')
                    is_initial = True
                    status['treated_as_initial'] = True

            email_sent = False

            # Proceed based on initial vs update
            if not is_initial:
                # Check if content actually changed
                if subscription.previous_calendar_hash == new_hash:
                    logger.info(f'No changes for {subscription.email}')
                    subscription.last_checked = datetime.now()
                    session.merge(subscription)
                    session.commit()
                    return status
                
                # Detect and notify changes
                email_sent = self.detect_and_notify_changes(subscription, previous_content, current_content)
                if email_sent:
                    status['email_queued'] = True
                    subscription.change_count += 1
                    subscription.last_change_detected = datetime.now()
            else:
                logger.info(f'Initial calendar for {subscription.email}')

            status['no_changes'] = False

            # Save new calendar to S3
            logger.info(f'Saving new calendar for {subscription.email}')
            calendar_local_path = self.save_calendar_to_s3(subscription.email, current_content)
            if not calendar_local_path:
                status['error'] = 'S3_ERROR'
                return status
            
            # Update subscription record
            subscription.previous_calendar_path = calendar_local_path
            subscription.previous_calendar_hash = new_hash
            subscription.last_checked = datetime.now() if not email_sent else subscription.last_change_detected

            session.commit()

            logger.info(f'Processed subscription for {subscription.email} successfully')
            return status
        
        except Exception as e:
            logger.exception(f'Error processing subscription for {sub.email}: {e}')
            session.rollback()
            status['error'] = 'UNDOCUMENTED_ERROR'
            return status
        finally:
            session.close()
