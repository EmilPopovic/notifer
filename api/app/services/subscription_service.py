from sqlalchemy.orm import Session
import logging

from shared.calendar_utils import parse_calendar_url, is_valid_ical_url
from shared.crud import create_subscription, get_subscription, update_activation, delete_user, update_paused
from shared.token_utils import decode_token, TokenExpiredError, TokenValidationError
from ..exceptions import (
    InvalidCalendarUrlError,
    SubscriptionAlreadyActiveError,
    SubscriptionNotFoundError,
    NotificationsAlreadyPausedError,
    NotificationsAlreadyActiveError,
    InvalidTokenError
)

logger = logging.getLogger(__name__)

class SubscriptionService:
    def __init__(self, db: Session, recipient_domain: str):
        self.db = db
        self.recipient_domain = recipient_domain

    def username_to_email(self, username: str) -> str:
        return f'{username}@{self.recipient_domain}'

    def create_subscription_from_url(self, calendar_url: str, language: str = 'hr', activated: bool = False) -> str:
        '''Create subscirption from calendar URL and return email.'''
        try:
            parsed_url = parse_calendar_url(calendar_url)
        except Exception as e:
            logger.error(f'Invalid calendar URL: {e}')
            raise InvalidCalendarUrlError(str(e))
        
        if not is_valid_ical_url(calendar_url):
            logger.error(f'Invalid iCal URL: {calendar_url}')
            raise InvalidCalendarUrlError('Invalid iCal at URL.')
        
        user = parsed_url['user']
        auth = parsed_url['auth']
        
        email = self.create_subscription_from_uname_and_auth(user, auth, language, activated)

        return email
    
    def create_subscription_from_uname_and_auth(self, username: str, auth: str, language: str = 'hr', activated: bool = False) -> str:
        email = self.username_to_email(username)
        existing = get_subscription(self.db, email)
        if existing:
            if existing.activated:
                logger.info(f'Subscirption already active: {email}')
                raise SubscriptionAlreadyActiveError()
            else:
                logger.info(f'Updating existing subscription: {email}')
                existing.calendar_auth = auth
                existing.language = language
                self.db.commit()

        else:
            logger.info(f'Creating new subscription: {email}')
            create_subscription(self.db, email, auth, language, activated)

        return email
    
    def validate_token(self, token: str, action: str) -> str:
        try:
            return decode_token(token, action)
        except (TokenExpiredError, TokenValidationError):
            logger.warning(f'Invalid {action} token: {token}')
            raise InvalidTokenError()
        
    def activate_subscription(self, email: str) -> bool:
        '''Activate subscription.'''
        subscription = update_activation(self.db, email, True)
        if not subscription:
            logger.error(f'Activation failed - not found: {email}')
            raise SubscriptionNotFoundError()
        
        logger.info(f'Subscription activated {email}')
        return True
    
    def delete_subscription(self, email: str) -> bool:
        '''Delete subscirption.'''
        success = delete_user(self.db, email)
        if not success:
            logger.error(f'Delete failed - not found: {email}')
            raise SubscriptionNotFoundError()
        
        logger.info(f'Subscription delted: {email}')
        return True
    
    def update_pause_status(self, email: str, paused: bool) -> bool:
        '''Update subscription pause status.'''
        subscription = update_paused(self.db, email, paused)
        if not subscription:
            logger.error(f'Pause update failed - not found: {email}')
            raise SubscriptionNotFoundError()
        
        action = 'paused' if paused else 'resumed'
        logger.info(f'Subscription {action}: {email}')
        return True
    
    def pause_subscription_by_username(self, username: str) -> bool:
        return self.update_pause_status(self.username_to_email(username), True)
    
    def resume_subscription_by_username(self, username: str) -> bool:
        return self.update_pause_status(self.username_to_email(username), False)
    
    def delete_subscription_by_username(self, username: str) -> bool:
        return self.delete_subscription(self.username_to_email(username))
    
    def get_subscription_info_by_username(self, username: str):
        sub = get_subscription(self.db, self.username_to_email(username))
        if not sub:
            raise SubscriptionNotFoundError()
        return {
            'email': sub.email,
            'activated': sub.activated,
            'paused': sub.paused,
            'created': sub.created,
            'language': sub.language,
            'last_checked': sub.last_checked
        }
    
    def validate_subscription_for_action(self, email: str, action: str) -> None:
        '''Validate subscription exists and is in correct state for action.'''
        subscription = get_subscription(self.db, email)
        if not subscription or not subscription.activated:
            raise SubscriptionNotFoundError()
        
        if action == 'pause' and subscription.paused:
            raise NotificationsAlreadyPausedError()
        elif action == 'resume' and not subscription.paused:
            raise NotificationsAlreadyActiveError()
        
    def get_user_language(self, email: str) -> str:
        '''Get user's preferred language, defaulting to Croatian.'''
        try:
            subscription = get_subscription(self.db, email)
            if subscription and subscription.language:
                return subscription.language
        except Exception as e:
            logger.warning(f'Could not get language for {email}: {e}')
        return 'hr'
