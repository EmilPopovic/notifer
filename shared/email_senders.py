import smtplib
import logging
from abc import ABC, abstractmethod
from datetime import date
from time import sleep
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import resend

from shared.email_templates import EmailContent
from shared.database import get_db
from shared.crud import (
    get_resend_usage_for_date,
    get_monthly_resend_usage,
    increment_resend_usage
)

logger = logging.getLogger(__name__)

class EmailSender(ABC):
    '''Abstract base class for email sending strategies.'''

    @abstractmethod
    def send_email(self, recipient_email: str, content: EmailContent) -> bool:
        '''Send an email. Returns True if successful, False otherwise.'''
        pass

class ResendEmailSender(EmailSender):
    '''Email sender using Resend API.'''

    def __init__(self, api_key: str, from_email: str, rate_limit_per_second: int = 2):
        self.api_key = api_key
        self.from_email = from_email
        self.rate_limit_per_second = rate_limit_per_second
        resend.api_key = api_key

    def send_email(self, recipient_email: str, content: EmailContent) -> bool:
        params: resend.Emails.SendParams = {
            'from': self.from_email,
            'to': [recipient_email],
            'subject': content.subject,
            'html': content.html
        }

        logger.info(f'Sending email via Resend to {recipient_email}')
        try:
            resend.Emails.send(params)
            logger.info(f'Email sent successfully via Resend to {recipient_email}')

            # Rate limiting
            if self.rate_limit_per_second > 0:
                delay = 1 / self.rate_limit_per_second
                logger.debug(f'Rate limiting: waiting {delay}s')
                sleep(delay)

            return True
        except Exception as e:
            logger.exception(f'Failed to send email via Resend to {recipient_email}: {e}')
            return False

class SMPTEmailSender(EmailSender):
    '''Email sender using SMTP.'''

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, from_email: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email

    def send_email(self, recipient_email: str, content: EmailContent) -> bool:
        logger.info(f'Sending email via SMTP to {recipient_email}')

        msg = MIMEMultipart('alternative')
        msg['Subject'] = content.subject
        msg['From'] = self.from_email
        msg['To'] = recipient_email
        msg.attach(MIMEText(content.html, 'html'))

        try:
            logger.debug(f'Connecting to SMTP server {self.smtp_server}:{self.smtp_port}')
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.from_email, recipient_email, msg.as_string())
            server.quit()
            logger.info(f'Email sent successfully via SMTP to {recipient_email}')
            return True
        except Exception as e:
            logger.exception(f'Failed to send email via SMTP to {recipient_email}: {e}')
            return False
        
class ResendWithUsageLimits:
    '''Helper class to manage Resend usage limits.'''

    def __init__(self, daily_limit: int = 95, monthly_limit: int = 2950):
        self.daily_limit = daily_limit
        self.monthly_limit = monthly_limit

    def can_send_with_resend(self) -> bool:
        today = date.today()
        start_of_month = today.replace(day=1)
        db = next(get_db())
        try:
            daily_count = get_resend_usage_for_date(db, today)
            monthly_count = get_monthly_resend_usage(db, start_of_month)

            if daily_count < self.daily_limit and monthly_count < self.monthly_limit:
                return True
            else:
                logger.info(f'Resend limits exceeded: daily {daily_count}/{self.daily_limit}, monthly {monthly_count}/{self.monthly_limit}')
                return False
        except Exception as e:
            logger.exception(f'Error checking Resend usage: {e}')
            return False
        finally:
            db.close()

    def update_usage(self):
        today = date.today()
        db = next(get_db())
        try:
            increment_resend_usage(db, today)
            logger.debug(f'Updated Resend usage for {today}')
        except Exception as e:
            logger.exception(f'Failed to update Resend usage: {e}')
            db.rollback()
        finally:
            db.close()

class ResendWithSMTPFallbackSender(EmailSender):
    '''Email sender that uses Resend with SMTP fallback based on usage limits.'''

    def __init__(self, resend_sender: ResendEmailSender, smtp_sender: SMPTEmailSender, usage_limits: ResendWithUsageLimits | None = None):
        self.resend_sender = resend_sender
        self.smtp_sender = smtp_sender
        self.usage_limits = usage_limits if usage_limits is not None else ResendWithUsageLimits()

    def send_email(self, recipient_email: str, content: EmailContent) -> bool:
        if self.usage_limits.can_send_with_resend():
            success = self.resend_sender.send_email(recipient_email, content)
            if success:
                self.usage_limits.update_usage()
                return True
            # If Resend fails, fall back to SMTP
            logger.warning(f'Resend failed for {recipient_email}, falling back to SMTP')
        else:
            logger.info(f'Resend limits reached, using SMTP fallback for {recipient_email}')

        return self.smtp_sender.send_email(recipient_email, content)
    