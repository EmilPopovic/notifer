import os
import redis
from rq import Queue
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from shared.calendar_utils import EventChange
from shared.token_utils import create_token
from shared.email_templates import (
    activation_email_content,
    deletion_email_content,
    pause_email_content,
    resume_email_content
)

redis_sync = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://redis:6379/0'))
email_queue = Queue('email', connection=redis_sync)

logger = logging.getLogger(__name__)


class EmailClient:
    
    def __init__(
            self,
            smtp_server: str,
            smtp_port: int,
            username: str,
            password: str,
            from_email: str,
            base_url: str,
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.base_url = base_url
        logger.info("EmailClient initialized with SMTP server %s:%s", smtp_server, smtp_port)

    def send_email_task(self, recipient_email: str, subject: str, body: str):
        logger.info('Executing email task: sending email to %s', recipient_email)
        self.__send_email(recipient_email, subject, body)
        
    def __enqueue_send(self, recipient_email: str, subject: str, body: str):
        email_queue.enqueue(self.send_email_task, recipient_email, subject, body)

    def __send_email(self, recipient_email: str, subject: str, body: str):
        logger.info("Preparing to send email to %s with subject: %s", recipient_email, subject)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = recipient_email

        msg.attach(MIMEText(body, 'html'))

        try:
            logger.debug("Connecting to SMTP server %s:%s", self.smtp_server, self.smtp_port)
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            logger.debug("Logging in as %s", self.username)
            server.login(self.username, self.password)
            logger.info("Sending email to %s", recipient_email)
            server.sendmail(self.from_email, recipient_email, msg.as_string())
            server.quit()
            logger.info("Successfully sent email to %s", recipient_email)
        except Exception as e:
            logger.exception("Failed to send email to %s: %s", recipient_email, e)

    def enqueue_send_activate_confirmation_email(self, recipient_email: str):
        logger.info("Sending activation confirmation email to %s", recipient_email)
        token = create_token(recipient_email, 'activate')
        subject, body = activation_email_content(self.base_url, token)
        self.__enqueue_send(recipient_email, subject, body)

    def enqueue_send_delete_confirmation_email(self, recipient_email: str):
        logger.info("Sending delete confirmation email to %s", recipient_email)
        token = create_token(recipient_email, 'delete')
        subject, body = deletion_email_content(self.base_url, token)
        self.__enqueue_send(recipient_email, subject, body)

    def enqueue_send_pause_confirmation_email(self, recipient_email: str):
        logger.info("Sending pause confirmation email to %s", recipient_email)
        token = create_token(recipient_email, 'pause')
        subject, body = pause_email_content(self.base_url, token)
        self.__enqueue_send(recipient_email, subject, body)

    def enqueue_send_resume_confirmation_email(self, recipient_email: str):
        logger.info("Sending resume confirmation email to %s", recipient_email)
        token = create_token(recipient_email, 'resume')
        subject, body = resume_email_content(self.base_url, token)
        self.__enqueue_send(recipient_email, subject, body)

    def enqueue_send_notification_email(self, recipient_email: str, event_changes: list[EventChange]):
        logger.info("Sending notification email to %s", recipient_email)
        token = create_token(recipient_email, 'pause')
        subject, body = notification_email_content(self.base_url, event_changes, token)
        self.__enqueue_send(recipient_email, subject, body)
