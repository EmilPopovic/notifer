import time
import logging
import threading
from enum import Enum
from typing import List
from queue import Queue
from dataclasses import dataclass
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
from shared.email_sender import EmailSender

logger = logging.getLogger(__name__)

class EmailType(Enum):
    ACTIVATE = 'activate'
    DELETE = 'delete'
    PAUSE = 'pause'
    RESUME = 'resume'
    NOTIFICATION = 'notification'

def get_email_queue_size() -> int:
    """
    Get the current size of the email queue.
    Can be called from any part of the application.
    """
    if EmailClient._queue_manager is not None:
        return EmailClient._queue_manager.get_queue_size()
    return 0

@dataclass
class EmailTask:
    recipient_email: str
    content: EmailContent
    sender: EmailSender

class EmailQueueManager:
    """Global email queue manager that handles rate limiting for all email clients."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, rate_limit_per_second: float = 2.0):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
        
    def __init__(self, rate_limit_per_second: float = 2.0):
        if self._initialized:
            return
        
        self.rate_limit_per_second = rate_limit_per_second
        self.min_interval = 1.0 / rate_limit_per_second
        self.email_queue = Queue()
        self.last_sent_time = 0
        self.queue_size = 0
        self.queue_size_lock = threading.Lock()

        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        
        self._initialized = True
        logger.info(f'EmailQueueManager initialized with rate limit: {rate_limit_per_second}/sec')

    def enqueue_email(self, recipient_email: str, content: EmailContent, sender: EmailSender) -> None:
        """Add email to the queue for sending."""
        task = EmailTask(recipient_email, content, sender)
        self.email_queue.put(task)

        with self.queue_size_lock:
            self.queue_size += 1

        logger.debug(f'Email queued for {recipient_email}, queue size: {self.queue_size}')

    def get_queue_size(self) -> int:
        """Get current queue size"""
        with self._lock:
            return self.queue_size
        
    def _worker(self):
        """Worker thread that processes the email queue with rate limiting."""
        logger.info('Email queue worker thread started')

        while True:
            try:
                # get next email task (blocks until available)
                task: EmailTask = self.email_queue.get()

                # ensure minimum interval between sends
                current_time = time.time()
                time_since_last = current_time - self.last_sent_time

                if time_since_last < self.min_interval:
                    sleep_time = self.min_interval - time_since_last
                    logger.debug(f'Rate limiting: sleeping for {sleep_time:.2f}s')
                    time.sleep(sleep_time)

                # send the email
                try:
                    logger.info(f'Sending email to {task.recipient_email}')
                    task.sender.send_email(task.recipient_email, task.content)
                    self.last_sent_time = time.time()
                    logger.info(f'Email sent successfully to {task.recipient_email}')

                except Exception as e:
                    logger.error(f'Failed to send email to {task.recipient_email}: {e}')
                
                finally:
                    # decrease queue size counter
                    with self.queue_size_lock:
                        self.queue_size = max(0, self.queue_size - 1)

                    # mark task as done
                    self.email_queue.task_done()
                
            except Exception as e:
                logger.error(f'Error in email worker thread: {e}')

class EmailClient:
    '''Unified email client that handles templating and async sending.'''
    _queue_manager: EmailQueueManager | None = None
    _queue_manager_lock = threading.Lock()

    def __init__(
            self, 
            email_sender: EmailSender, 
            api_base_url: str,
            rate_limit_per_second: float = 2.0
    ) -> None:
        self.email_sender = email_sender
        self.api_base_url = api_base_url

        # initialize the global queue manager if not already done
        with EmailClient._queue_manager_lock:
            if EmailClient._queue_manager is None:
                EmailClient._queue_manager = EmailQueueManager(rate_limit_per_second)

        logger.info(f'EmailClient initialized with {type(email_sender).__name__}')

    def _enqueue_email(self, recipient_email: str, content: EmailContent) -> None:
        '''Queue an email for async sending.'''
        if self._queue_manager is not None:
            self._queue_manager.enqueue_email(recipient_email, content, self.email_sender)

    def get_queue_size(self) -> int:
        """Get the current email queue size."""
        if self._queue_manager is not None:
            return self._queue_manager.get_queue_size()
        return 0

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
    
    def send_confirmation_email(self, email_type: EmailType, recipient_email: str, language: str = 'hr') -> None:
        '''Send a confirmation email (activation, deletion, pause, resume).'''
        logger.info(f'Sending {email_type.value} email to {recipient_email} in {language}')

        content = self._generate_confirmation_email(email_type, recipient_email, language)
        self._enqueue_email(recipient_email, content)

    def send_notification_email(self, recipient_email: str, event_changes: List[EventChange], language: str = 'hr') -> None:
        '''Send a notification email about schedule changes.'''
        logger.info(f'Sending notification email to {recipient_email} in {language}')

        token = create_token(recipient_email, 'pause')  # For unsubscribe link
        content = notification_email_content(self.api_base_url, event_changes, token, language)
        self._enqueue_email(recipient_email, content)
