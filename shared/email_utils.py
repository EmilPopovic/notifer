import os
from time import sleep

import redis
import resend
from rq import Queue
import smtplib
import logging
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from shared.calendar_utils import EventChange
from shared.token_utils import create_token
from shared.email_templates import (
    activation_email_content,
    deletion_email_content,
    pause_email_content,
    resume_email_content,
    notification_email_content
)
from shared.database import get_db
from shared.crud import  (
    get_resend_usage_for_date,
    get_monthly_resend_usage,
    increment_resend_usage
)

redis_sync = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://redis:6379/0'))
email_queue = Queue('email', connection=redis_sync)

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


RESEND_DAILIY_LIMIT = 95
RESEND_MONTLY_LIMIT = 2950
RESEND_SECOND_LIMIT = 2


def can_send_with_resend() -> bool:
    today = date.today()
    start_of_month = today.replace(day=1)
    db = next(get_db())
    try:
        daily_count = get_resend_usage_for_date(db, today)
        monthly_count = get_monthly_resend_usage(db, start_of_month)
        if daily_count < RESEND_DAILIY_LIMIT and monthly_count < RESEND_MONTLY_LIMIT:
            return True
        else:
            logger.info(f'Resend limits exceeded: daily {daily_count}/{RESEND_DAILIY_LIMIT}, monthly {monthly_count}/{RESEND_MONTLY_LIMIT}')
            return False
    except Exception as e:
        logger.exception(f'Error checking Resend usage: {e}')
        return False
    finally:
        db.close()


def update_usage():
    today = date.today()
    db = next(get_db())
    try:
        increment_resend_usage(db, today)
        logger.debug(f'Updated Resend usage for {today}',)
    except Exception as e:
        logger.exception(f'Failed to update Resend usage: {e}')
        db.rollback()
    finally:
        db.close()


class EmailClient:
    def __init__(
            self,
            resend_from_email: str,
            resend_api_key: str,
            fallback_smtp_server: str,
            fallback_smtp_port: int,
            fallback_username: str,
            fallback_password: str,
            fallback_from_email: str,
            api_base_url: str,
    ):
        self.resend_from_email = resend_from_email
        self.resend_api_key = resend_api_key
        self.fallback_smtp_server = fallback_smtp_server
        self.fallback_smtp_port = fallback_smtp_port
        self.fallback_username = fallback_username
        self.fallback_password = fallback_password
        self.fallback_from_email = fallback_from_email
        self.api_base_url = api_base_url
        
        resend.api_key = resend_api_key
        
        logger.info(f'EmailClient initialized for {resend_from_email}, api key [hidden]{resend.api_key[-3:]} with fallback to {fallback_from_email} at {fallback_smtp_server}:{fallback_smtp_port}')


    def __enqueue_send(self, recipient_email: str, subject: str, body: str):
        email_queue.enqueue(self.send_email_task, recipient_email, subject, body)
        
        
    def send_email_task(self, recipient_email: str, subject: str, body: str):
        logger.info('Executing email task: sending email to %s', recipient_email)
        self.__send_email(recipient_email, subject, body)


    def __send_email(self, recipient_email: str, subject: str, body: str):
        if can_send_with_resend():
            self.__send_with_resend(recipient_email, subject, body)
            update_usage()
        else:
            logger.info(f'Resend limit reached, falling back to {self.fallback_smtp_server} for {recipient_email}')
            self.__send_with_fallback(recipient_email, subject, body)
            
            
    def __send_with_resend(self, recipient_email: str, subject: str, body: str):
        resend.api_key = self.resend_api_key
        params: resend.Emails.SendParams = {
            'from': self.resend_from_email,
            'to': [recipient_email],
            'subject': subject,
            'html': body,
        }
        logger.info(f'Sending resend email to {recipient_email} with api key [hidden]{resend.api_key[-3:]}')
        try:
            resend.Emails.send(params)
            logger.info(f'Email sent via Resend to {recipient_email}')
            delay = 1 / RESEND_SECOND_LIMIT
            logger.info(f'Waiting for Resend delay: {delay}s')
            sleep(delay)
        except Exception as e:
            logger.exception(f'Failed to send email via Resend to {recipient_email}: {e}')
    
        
    def __send_with_fallback(self, recipient_email: str, subject: str, body: str):    
        logger.info(f'Preparing to send email via fallback to {recipient_email} with subject {subject}')
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.fallback_from_email
        msg['To'] = recipient_email
        msg.attach(MIMEText(body, 'html'))

        try:
            logger.debug(f'Connecting to SMTP server {self.fallback_smtp_server}:{self.fallback_smtp_port}')
            server = smtplib.SMTP(self.fallback_smtp_server, self.fallback_smtp_port)
            server.starttls()
            logger.info(f'Logging in as {self.fallback_username} with passwrod [hidden]{self.fallback_password[-3:]}')
            server.login(self.fallback_username, self.fallback_password)
            logger.info('Sending email to %s', recipient_email)
            server.sendmail(self.fallback_from_email, recipient_email, msg.as_string())
            server.quit()
            logger.info('Successfully sent email to %s', recipient_email)
        except Exception as e:
            logger.exception('Failed to send email to %s: %s', recipient_email, e)

    def enqueue_send_activate_confirmation_email(self, recipient_email: str):
        logger.info('Sending activation confirmation email to %s', recipient_email)
        token = create_token(recipient_email, 'activate')
        subject, body = activation_email_content(self.api_base_url, token)
        self.__enqueue_send(recipient_email, subject, body)


    def enqueue_send_delete_confirmation_email(self, recipient_email: str):
        logger.info('Sending delete confirmation email to %s', recipient_email)
        token = create_token(recipient_email, 'delete')
        subject, body = deletion_email_content(self.api_base_url, token)
        self.__enqueue_send(recipient_email, subject, body)


    def enqueue_send_pause_confirmation_email(self, recipient_email: str):
        logger.info('Sending pause confirmation email to %s', recipient_email)
        token = create_token(recipient_email, 'pause')
        subject, body = pause_email_content(self.api_base_url, token)
        self.__enqueue_send(recipient_email, subject, body)


    def enqueue_send_resume_confirmation_email(self, recipient_email: str):
        logger.info('Sending resume confirmation email to %s', recipient_email)
        token = create_token(recipient_email, 'resume')
        subject, body = resume_email_content(self.api_base_url, token)
        self.__enqueue_send(recipient_email, subject, body)


    def enqueue_send_notification_email(self, recipient_email: str, event_changes: list[EventChange]):
        logger.info('Sending notification email to %s', recipient_email)
        token = create_token(recipient_email, 'pause')
        subject, body = notification_email_content(self.api_base_url, event_changes, token)
        self.__enqueue_send(recipient_email, subject, body)
