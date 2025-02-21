import os
import time
import logging

import requests
import hashlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from shared.calendar_utils import is_valid_ical, compute_ical_changes
from shared.database import SessionLocal
from shared.models import UserCalendar
from shared.email_utils import EmailClient
from shared.secrets import get_secret

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

WORKER_INTERVAL = 300
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


def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def fetch_calendar_with_retry(url: str, retries: int = 3, backoff_factor: float = 1.0) -> str | None:
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                logger.warning('Non-200 status code %s when fetching %s', response.status_code, url)
        except Exception as e:
            logger.exception('Exception fetching %s: %s', url, e)
        
        sleep_time = backoff_factor * (2 ** (attempt - 1))
        logger.info('Retrying in %s seconds.', sleep_time)
        time.sleep(sleep_time)
    return None


def process_subscription(subscription: UserCalendar):
    session = SessionLocal()
    try:
        if not subscription.activated or subscription.paused:
            logger.info('Skipping %s (not activated or paused)', subscription.email)
            return
        
        calendar_url = f'{BASE_CALENDAR_URL}?user={subscription.email.split('@')[0]}&auth={subscription.calendar_auth}'
        logger.info('Fetching calendar for %s from %s', subscription.email, calendar_url)

        calendar_content = fetch_calendar_with_retry(calendar_url)
        if calendar_content is None:
            logger.error('Failed to fetch calendar for %s after retries', subscription.email)
            return
        
        if not is_valid_ical(calendar_content):
            logger.error('Fetched calendar for %s is not a valid iCal document', subscription.email)
            return
        
        new_hash = compute_hash(calendar_content)
        
        if subscription.previous_calendar_hash is None:
            logger.info('Storing initial calendar for %s', subscription.email)
            subscription.previous_calendar = calendar_content
            subscription.previous_calendar_hash = new_hash
            subscription.last_checked = datetime.now()
            session.merge(subscription)
            session.commit()
            return
        
        if subscription.previous_calendar_hash == new_hash:
            logger.info('No changes detected for %s', subscription.email)
            subscription.last_checked = datetime.now()
            session.merge(subscription)
            session.commit()
            return
        
        event_changes = compute_ical_changes(old_ical=subscription.previous_calendar, new_ical=calendar_content)
        if not event_changes:
            logger.info('Calendar content changed but no event differences found for %s', subscription.email)
        else:
            logger.info('Detected %s event changes for %s', len(event_changes), subscription.email)
            email_client.enqueue_send_notification_email(subscription.email, event_changes)
        
        subscription.previous_calendar = calendar_content
        subscription.previous_calendar_hash = new_hash
        subscription.last_checked = datetime.now()
        session.merge(subscription)
        session.commit()
        
        logger.info('Processed subscription for %s successfully', subscription.email)
    
    except Exception as e:
        logger.exception('Error processing subscription for %s: %s', subscription.email, e)
        session.rollback()
    finally:
        session.close()
        
        
def main_loop():
    logger.info('Worker started with a %s-second interval', WORKER_INTERVAL)
    while True:
        session = SessionLocal()
        subscriptions = []
        try:
            subscriptions = session.query(UserCalendar).all()
            session.expunge_all()
        except Exception as e:
            logger.exception('Error retrieving subscriptions: %s', e)
            session.close()
            time.sleep(WORKER_INTERVAL)
            continue
        finally:
            session.close()
            
        logger.info('Found %s subscriptions', len(subscriptions))
            
        if not subscriptions:
            logger.info('No subscriptions found. Sleeping for %s seconds.', WORKER_INTERVAL)
            time.sleep(WORKER_INTERVAL)
            continue
            
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(process_subscription, sub): sub for sub in subscriptions}
            for future in as_completed(futures):
                sub = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.exception('Unhandled error processing subscription for %s: %s', sub.email, e)
                    
        logger.info('Cycle complete. Sleeping for %s seconds.', WORKER_INTERVAL)
        time.sleep(WORKER_INTERVAL)


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        logger.info('Worker shutdown requested (KeyboardInterrupt). Exiting.')
