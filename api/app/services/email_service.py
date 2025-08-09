import logging
from typing import Protocol, List

from shared.calendar_utils import EventChange
from shared.email_client import EmailType

logger = logging.getLogger(__name__)

class EmailClientProtocol(Protocol):
    def send_confirmation_email(self, email_type: EmailType, recipient_email: str, language: str) -> None: ...
    def send_notification_email(self, recipient_email: str, event_changes: List[EventChange], language: str) -> None: ...

class EmailService:
    '''High-level email service for the API.'''

    def __init__(self, email_client: EmailClientProtocol):
        self.email_client = email_client

    def send_activation_email(self, email: str, language: str = 'hr') -> None:
        '''Send activation confirmation email.'''
        logger.info(f'Sending activation email to: {email} in language {language}')
        self.email_client.send_confirmation_email(EmailType.ACTIVATE, email, language)

    def send_deletion_email(self, email: str, language: str = 'hr') -> None:
        '''Send deletion confirmation email.'''
        logger.info(f'Sending deletion email to: {email} in language {language}')
        self.email_client.send_confirmation_email(EmailType.DELETE, email, language)

    def send_pause_email(self, email: str, language: str = 'hr') -> None:
        '''Send pause confirmation email.'''
        logger.info(f'Sending pause email to: {email} in language {language}')
        self.email_client.send_confirmation_email(EmailType.PAUSE, email, language)

    def send_resume_email(self, email: str, language: str = 'hr') -> None:
        '''Send resume confirmation email.'''
        logger.info(f'Sending resume email to: {email} in language {language}')
        self.email_client.send_confirmation_email(EmailType.RESUME, email, language)
