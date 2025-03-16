import os
import time
import logging

import requests
import hashlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from shared.calendar_utils import is_valid_ical, compute_ical_changes
from shared.database import SessionLocal, init_db
from shared.models import UserCalendar
from shared.email_utils import EmailClient
from shared.secrets import get_secret
from shared.s3_utils import S3Utils

import redis
from rq import Queue

LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | "
    "%(funcName)s() | %(threadName)s | %(message)s"
)

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

WORKER_INTERVAL = int(os.getenv('WORKER_INTERVAL', 60 * 60))  # interval set in env, default to 1 hour if not
BASE_CALENDAR_URL = 'https://www.fer.unizg.hr/_download/calevent/mycal.ics'

email_client = EmailClient(
    resend_from_email=os.getenv('UPDATE_USERNAME'),
    resend_api_key=get_secret('RESEND_API_KEY_FILE'),
    fallback_smtp_server=os.getenv('SMTP_SERVER'),
    fallback_smtp_port=int(os.getenv('SMTP_PORT', 587)),
    fallback_username=os.getenv('UPDATE_FALLBACK_USERNAME'),
    fallback_password=get_secret('UPDATE_PASSWORD_FILE'),
    fallback_from_email=os.getenv('UPDATE_USERNAME'),
    api_base_url=os.getenv('API_URL').replace('${API_PORT}', str(os.getenv('API_PORT'))),
)

redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
redis_conn = redis.Redis.from_url(redis_url)
email_queue = Queue('email', connection=redis_conn)

s3 = S3Utils(
    endpoint_url=os.getenv('S3_ENDPOINT'),
    aws_access_key_id=os.getenv('S3_USER'),
    aws_secret_access_key=get_secret('S3_PASSWORD_FILE'),
    bucket_name=os.getenv('S3_BUCKET')
)


def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def fetch_calendar_with_retry(url: str, retries: int = 3, backoff_factor: float = 30) -> str | None:
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f'Non-200 status code {response.status_code} when fetching {url}')
        except Exception as e:
            logger.exception(f'Exception fetching {url}: {e}')
        
        sleep_time = backoff_factor * (2 ** (attempt - 1))
        logger.info(f'Retrying in {sleep_time} seconds.')
        time.sleep(sleep_time)
    return None


def process_subscription(subscription: UserCalendar):
    session = SessionLocal()
    try:
        if not subscription.activated or subscription.paused:
            logger.info(f'Skipping {subscription.email} (not activated or paused)')
            return
        
        true_calendar_url = f'{BASE_CALENDAR_URL}?user={subscription.email.split('@')[0]}&auth={subscription.calendar_auth}'
        logger.info(f'Fetching calendar for {subscription.email} from {true_calendar_url}')

        true_calendar_content = fetch_calendar_with_retry(true_calendar_url)
        if true_calendar_content is None:
            logger.error(f'Failed to fetch calendar for {subscription.email} after retries')
            return
        
        if not is_valid_ical(true_calendar_content):
            logger.error(f'Fetched calendar for {subscription.email} is not a valid iCal document')
            return
        
        new_hash = compute_hash(true_calendar_content)

        is_initial = True
        previous_calendar_content = None
        if subscription.previous_calendar_url:
            is_initial = False
            previous_calendar_content = s3.get_calendar(subscription.email)
            if previous_calendar_content is None:
                logger.warning(f'Previous calendar missing or failed from S3 for {subscription.email}, treating as new')
                is_initial = True

        if not is_initial:

            if subscription.previous_calendar_hash == new_hash:
                logger.info(f'No changes for {subscription.email}')
                subscription.last_checked = datetime.now()
                session.merge(subscription)
                session.commit()
                return

            event_changes = compute_ical_changes(
                old_ical=previous_calendar_content,
                new_ical=true_calendar_content
            ) if previous_calendar_content else None

            if event_changes:
                logger.info(f'Detected {len(event_changes)} event changes for {subscription.email}')
                email_client.enqueue_send_notification_email(subscription.email, event_changes)
            else:
                logger.info(f'Calendar content changed but no event differences found for {subscription.email}')

        else:
            logger.info(f'Inital calendar for {subscription.email}')

        logger.info(f'Saving new calendar for {subscription.email}')
        calendar_s3_url = s3.save_calendar(subscription.email, true_calendar_content)
        if calendar_s3_url:
            subscription.previous_calendar_url = calendar_s3_url
            subscription.previous_calendar_hash = new_hash
        else:
            logger.error(f'Failed to upload updated calendar for {subscription.email} to S3')
            return

        subscription.last_checked = datetime.now()
        session.merge(subscription)
        session.commit()
        
        logger.info(f'Processed subscription for {subscription.email} successfully')
    
    except Exception as e:
        logger.exception(f'Error processing subscription for {subscription.email}: {e}')
        session.rollback()
    finally:
        session.close()
        
        
def main_loop():
    logger.info(f'Worker started with a {WORKER_INTERVAL}-second interval')
    while True:
        session = SessionLocal()
        subscriptions = []
        try:
            subscriptions = session.query(UserCalendar).all()
            session.expunge_all()
        except Exception as e:
            logger.exception(f'Error retrieving subscriptions: {e}')
            session.close()
            time.sleep(WORKER_INTERVAL)
            continue
        finally:
            session.close()
            
        logger.info(f'Found {len(subscriptions)} subscriptions')
            
        if not subscriptions:
            logger.info(f'No subscriptions found. Sleeping for {WORKER_INTERVAL} seconds.')
            time.sleep(WORKER_INTERVAL)
            continue
            
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(process_subscription, sub): sub for sub in subscriptions}
            for future in as_completed(futures):
                sub = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.exception(f'Unhandled error processing subscription for {sub.email}: {e}')
                    
        logger.info(f'Cycle complete. Sleeping for {WORKER_INTERVAL} seconds.')
        time.sleep(WORKER_INTERVAL)


if __name__ == '__main__':
    time.sleep(5)
    init_db()
    try:
        main_loop()
    except KeyboardInterrupt:
        logger.info('Worker shutdown requested (KeyboardInterrupt). Exiting.')
