from functools import lru_cache

from shared.s3_client import S3Client
from shared.email_client import EmailClient
from shared.email_client_factory import EmailClientFactory, EmailStrategy
from .config import get_settings
from .services.calendar_service import CalendarService
from .services.worker_service import WorkerService

_s3_client: S3Client | None = None
_email_client: EmailClient | None = None
_calendar_service: CalendarService | None = None
_worker_service: WorkerService | None = None

@lru_cache
def get_s3_client() -> S3Client:
    '''Get S3 client instance.'''
    global _s3_client
    if _s3_client is None:
        settings = get_settings()
        _s3_client = S3Client(
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_user,
            aws_secret_access_key=settings.s3_password,
            bucket_name=settings.s3_bucket
        )
    return _s3_client

@lru_cache()
def get_email_client() -> EmailClient:
    '''Get email client singleton based on configuration.'''
    global _email_client
    if _email_client is not None:
        return _email_client

    settings = get_settings()

    if settings.email_strategy == EmailStrategy.RESEND_ONLY:
        _email_client = EmailClientFactory.create_resend_only_client(
            api_key=settings.resend_api_key,
            from_email=settings.resend_username,
            api_base_url=settings.api_url
        )
    elif settings.email_strategy == EmailStrategy.SMTP_ONLY:
        _email_client = EmailClientFactory.create_smtp_only_client(
            smtp_server=settings.smtp_server,
            smtp_port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            from_email=settings.smtp_username,
            api_base_url=settings.api_url
        )
    else:  # RESEND_WITH_FALLBACK (default)
        _email_client = EmailClientFactory.create_resend_with_smtp_fallback(
            resend_api_key=settings.resend_api_key,
            resend_from_email=settings.resend_username,
            smtp_server=settings.smtp_server,
            smtp_port=settings.smtp_port,
            smtp_username=settings.smtp_username,
            smtp_password=settings.smtp_password,
            smtp_from_email=settings.smtp_username,
            api_base_url=settings.api_url
        )

    return _email_client

@lru_cache()
def get_calendar_service() -> CalendarService:
    '''Get calendar service instance.'''
    global _calendar_service
    if _calendar_service is None:
        settings = get_settings()
        _calendar_service = CalendarService(
            s3_client=get_s3_client(),
            email_client=get_email_client(),
            base_calendar_url=settings.base_calendar_url
        )
    return _calendar_service

@lru_cache
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
