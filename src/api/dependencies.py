from fastapi import Depends, Header, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi_throttle import RateLimiter
from sqlalchemy.orm import Session
from functools import lru_cache
import hashlib

from shared.database import get_db
from shared.email_client import EmailClient
from shared.email_client_factory import EmailClientFactory, EmailStrategy
from shared.storage_manager import StorageManager
from .config import get_settings
from .services.subscription_service import SubscriptionService
from .services.template_service import TemplateService
from .services.email_service import EmailService
from .middleware import get_rate_limiter

# Global instances
_email_client: EmailClient | None = None
_storage_manager: StorageManager | None = None
_templates: Jinja2Templates | None = None

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

@lru_cache
def get_storage_manager() -> StorageManager:
    '''Get storage manager singleton.'''
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = StorageManager()
    return _storage_manager

def get_templates() -> Jinja2Templates:
    '''Get Jinja2 templates.'''
    global _templates
    if _templates is None:
        _templates = Jinja2Templates(directory='templates')
    return _templates

def get_subscription_service(db: Session = Depends(get_db)) -> SubscriptionService:
    '''Get subscription service instance.'''
    settings = get_settings()
    return SubscriptionService(db, settings.recipient_domain)

def get_template_service() -> TemplateService:
    '''Get template service instance.'''
    templates = get_templates()
    settings = get_settings()
    return TemplateService(templates, settings.api_url)

def get_email_service(email_client = Depends(get_email_client)) -> EmailService:
    '''Get email service instance.'''
    return EmailService(email_client)

async def rate_limit_dependency() -> RateLimiter:
    '''Rate limiter dependency.'''
    limiter = get_rate_limiter()
    return limiter

def verify_notifer_token(authorization: str = Header(...)):
    if not authorization.startswith('Bearer'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token format')
    token = authorization.removeprefix('Bearer ').strip()
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    settings = get_settings()
    if token_hash != settings.notifer_api_token_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid API token')
