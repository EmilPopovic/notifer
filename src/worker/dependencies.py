from shared.storage_manager import StorageManager
from shared.email_client import EmailClient
from shared.email_client_factory import EmailClientFactory
from config import get_settings
from worker.services.calendar_service import CalendarService
from worker.services.worker_service import WorkerService

_storage_manager: StorageManager | None = None
_email_client: EmailClient | None = None
_calendar_service: CalendarService | None = None
_worker_service: WorkerService | None = None

def get_storage_manager() -> StorageManager:
    '''Get storage manager instance.'''
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = StorageManager()
    return _storage_manager

def get_email_client() -> EmailClient:
    '''Get email client singleton based on configuration.'''
    global _email_client
    if _email_client is None:
        settings = get_settings()
        _email_client = EmailClientFactory.create_smtp_client(
            smtp_server=settings.smtp_server,
            smtp_port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            from_email=settings.smtp_sender_email,
            api_base_url=settings.api_url
        )
    return _email_client

def get_calendar_service() -> CalendarService:
    '''Get calendar service instance.'''
    global _calendar_service
    if _calendar_service is None:
        settings = get_settings()
        _calendar_service = CalendarService(
            storage_manager=get_storage_manager(),
            email_client=get_email_client(),
            base_calendar_url=settings.base_calendar_url
        )
    return _calendar_service

def get_worker_service() -> WorkerService:
    '''Get worker service instance.'''
    global _worker_service
    if _worker_service is None:
        settings = get_settings()
        _worker_service = WorkerService(
            calendar_service=get_calendar_service(),
            worker_interval=settings.worker_interval,
            max_workers=settings.max_workers
        )
    return _worker_service
