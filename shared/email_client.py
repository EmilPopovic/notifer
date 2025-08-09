import os
import logging
from enum import Enum
from typing import List

import redis
from rq import Queue

from shared.calendar_utils import EventChange
from shared.token_utils import create_token
from shared.email_templates import (
    EmailContent,
    activation_email_content,
    deletion_email_content,
    pause_email_content,
    resume_email_content,
    notification_email_content
)
from shared.email_senders import EmailSender

logger = logging.getLogger(__name__)

class EmailType(Enum):
    ACTIVATE = 'activate'
    DELETE = 'delete'
    PAUSE = 'pause'
    RESUME = 'resume'
    NOTIFICATION = 'notification'

def send_email_task(recipient_email: str, content_dict: dict, sender_config: dict):
    '''Worker task for sending asynchronously.'''
    logger.info(f'Executing email task: sending email to {recipient_email}')

    # Recreate the email sender from config to avoid serializing the sender object
    from shared.email_client_factory import EmailClientFactory

    if sender_config['type'] == 'resend_only':
        sender = EmailClientFactory.create_resend_only_client(**sender_config['params']).email_sender
    elif sender_config['type'] == 'smtp_only':
        sender = EmailClientFactory.create_smtp_only_client(**sender_config['params']).email_sender
    else:  # resend_with_fallback
        sender = EmailClientFactory.create_resend_with_smtp_fallback(**sender_config['params']).email_sender

    # Create content and send
    content = EmailContent(
        subject=content_dict['subject'],
        html=content_dict['html']
    )
    sender.send_email(recipient_email, content)

class EmailClient:
    '''Unified email client that handles templating and async sending.'''

    def __init__(
            self, 
            email_sender: EmailSender, 
            api_base_url: str, 
            redis_url: str | None = None, 
            sender_config: dict | None = None
    ):
        self.email_sender = email_sender
        self.api_base_url = api_base_url
        self.sender_config = sender_config

        # Setup Redis queue for async sending
        redis_url = redis_url if redis_url is not None else os.environ.get('REDIS_URL', 'redis://redis:6379/0')
        redis_client = redis.Redis.from_url(redis_url)
        self.email_queue = Queue('email', connection=redis_client)

        logger.info(f'EmailClient initialized with {type(email_sender).__name__}')

    def _enqueue_email(self, recipient_email: str, content: EmailContent):
        '''Queue an email for async sending.'''
        content_dict = {
            'subject': content.subject,
            'html': content.html
        }
        self.email_queue.enqueue(send_email_task, recipient_email, content_dict, self.sender_config)

    def _generate_confirmation_email(self, email_type: EmailType, recipient_email: str, language: str) -> EmailContent:
        '''Generate confirmation email content.'''
        token = create_token(recipient_email, email_type.value)

        email_generators = {
            EmailType.ACTIVATE: activation_email_content,
            EmailType.DELETE: deletion_email_content,
            EmailType.PAUSE: pause_email_content,
            EmailType.RESUME: resume_email_content,
        }

        generator = email_generators.get(email_type)
        if not generator:
            raise ValueError(f'Unsupported email type: {email_type}')
        
        return generator(self.api_base_url, token, language)
    
    def send_confirmation_email(self, email_type: EmailType, recipient_email: str, language: str = 'hr'):
        '''Send a confirmation email (activation, deletion, pause, resume).'''
        logger.info(f'Sending {email_type.value} email to {recipient_email} in {language}')

        content = self._generate_confirmation_email(email_type, recipient_email, language)
        self._enqueue_email(recipient_email, content)

    def send_notification_email(self, recipient_email: str, event_changes: List[EventChange], language: str = 'hr'):
        '''Send a notification email about schedule changes.'''
        logger.info(f'Sending notification email to {recipient_email} in {language}')

        token = create_token(recipient_email, 'pause')  # For unsubscribe link
        content = notification_email_content(self.api_base_url, event_changes, token, language)
        self._enqueue_email(recipient_email, content)
