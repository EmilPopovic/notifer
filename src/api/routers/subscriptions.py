import logging
from fastapi import APIRouter, Body, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi_throttle import RateLimiter
from api.dependencies import (
    SubscriptionService,
    EmailService,
    TemplateService,
    StorageManager,
    get_subscription_service,
    get_email_service,
    get_template_service,
    get_storage_manager,
    rate_limit_dependency,
    require_component_enabled,
)
from api.schemas import SubscriptionResponse, EmailSentResponse
from api.exceptions import InvalidTokenError, ErrorCode

logger = logging.getLogger(__name__)
router = APIRouter(tags=['subscriptions'])

def handle_token_error(
        e: InvalidTokenError,
        request: Request,
        token: str,
        action: str,
        subscription_service: SubscriptionService,
        template_service: TemplateService
) -> HTMLResponse:
    '''Handle localized errors with proper language detection.'''
    user_language = template_service._get_locale(request)  # Browser fallback

    try:
        # Try to extract email from token to get user's preferred language
        email = subscription_service.validate_token(token, action)
        user_language = subscription_service.get_user_language(email)
    except Exception as _:
        pass  # Keep browser detection fallback

    return template_service.render_error(request, None, str(e.detail), language=user_language, error_type=ErrorCode.INVALID_TOKEN)

@router.post('/subscribe', response_model=SubscriptionResponse,
             dependencies=[require_component_enabled('student_signup_enabled')])
async def subscribe(
        q: str,
        language: str = 'hr',
        subscription_service: SubscriptionService = Depends(get_subscription_service),
        email_service: EmailService = Depends(get_email_service),
        _rate_limit: RateLimiter = Depends(rate_limit_dependency)
):
    logger.info(f'Subscription request: {q[:30]}..., language: {language}')
    email = subscription_service.create_subscription_from_url(q, language)
    email_service.send_activation_email(email, language)

    logger.info(f'Subscritpion created: {email} with language: {language}')
    return SubscriptionResponse(status='ok', email=email)

@router.get('/activate', response_class=HTMLResponse,
            dependencies=[require_component_enabled('student_signup_enabled')])
async def activate (
        request: Request,
        token: str,
        subscription_service: SubscriptionService = Depends(get_subscription_service),
        template_service: TemplateService = Depends(get_template_service)
):
    logger.info('Activation request')
    try:
        email = subscription_service.validate_token(token, 'activate')

        user_language = subscription_service.get_user_language(email)

        subscription_service.activate_subscription(email)
        return template_service.render_activate(request, language=user_language)
    except InvalidTokenError as e:
        return handle_token_error(e, request, token, 'activate', subscription_service, template_service)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.post('/request-delete',
             dependencies=[require_component_enabled('student_delete_enabled')])
async def request_delete(
        email: str = Body(..., embed=True),
        subscription_service: SubscriptionService = Depends(get_subscription_service),
        email_service: EmailService = Depends(get_email_service),
        _rate_limit: RateLimiter = Depends(rate_limit_dependency)
):
    logger.info(f'Delete request: {email}')
    subscription_service.validate_subscription_for_action(email, 'delete')

    user_language = subscription_service.get_user_language(email)
    email_service.send_deletion_email(email, user_language)

    return EmailSentResponse(message='Deletion confirmation email sent.')

@router.get('/delete', response_class=HTMLResponse,
            dependencies=[require_component_enabled('student_delete_enabled')])
async def delete_account(
        request: Request,
        token: str,
        subscription_service: SubscriptionService = Depends(get_subscription_service),
        template_service: TemplateService = Depends(get_template_service),
        storage: StorageManager = Depends(get_storage_manager)
):
    logger.info('Delete account request')
    try:
        email = subscription_service.validate_token(token, 'delete')
        user_language = subscription_service.get_user_language(email)

        subscription_service.delete_subscription(email)
        storage.delete_calendar(email)

        return template_service.render_delete(request, email, language=user_language)
    except InvalidTokenError as e:
        return handle_token_error(e, request, token, 'delete', subscription_service, template_service)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.post('/request-pause',
             dependencies=[require_component_enabled('student_pause_enabled')])
async def request_pause(
        email: str = Body(..., embed=True),
        subscription_service: SubscriptionService = Depends(get_subscription_service),
        email_service: EmailService = Depends(get_email_service),
        _rate_limit: RateLimiter = Depends(rate_limit_dependency)
) -> EmailSentResponse:
    logger.info(f'Pause request: {email}')
    subscription_service.validate_subscription_for_action(email, 'pause')

    user_language = subscription_service.get_user_language(email)
    email_service.send_pause_email(email, user_language)

    return EmailSentResponse(message='Pause confirmation email sent.')

@router.get('/pause', response_class=HTMLResponse,
            dependencies=[require_component_enabled('student_pause_enabled')])
async def pause_notifications(
        request: Request,
        token: str,
        subscription_service: SubscriptionService = Depends(get_subscription_service),
        template_service: TemplateService = Depends(get_template_service),
        storage: StorageManager = Depends(get_storage_manager)
):
    logger.info('Pause notifications request')
    try:
        email = subscription_service.validate_token(token, 'pause')
        user_language = subscription_service.get_user_language(email)

        subscription_service.update_pause_status(email, True)
        storage.delete_calendar(email)

        return template_service.render_pause(request, email, language=user_language)
    except InvalidTokenError as e:
        return handle_token_error(e, request, token, 'pause', subscription_service, template_service)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.post('/request-resume',
             dependencies=[require_component_enabled('student_resume_enabled')])
async def request_resume(
        email: str = Body(..., embed=True),
        subscription_service: SubscriptionService = Depends(get_subscription_service),
        email_service: EmailService = Depends(get_email_service),
        _rate_limit: RateLimiter = Depends(rate_limit_dependency)
):
    logger.info(f'Resume request: {email}')
    subscription_service.validate_subscription_for_action(email, 'resume')

    user_language = subscription_service.get_user_language(email)
    email_service.send_resume_email(email, user_language)

    return EmailSentResponse(message='Resume confirmation email sent.')

@router.get('/resume', response_class=HTMLResponse,
            dependencies=[require_component_enabled('student_resume_enabled')])
async def resume_notifications(
        request: Request,
        token: str,
        subscription_service: SubscriptionService = Depends(get_subscription_service),
        template_service: TemplateService = Depends(get_template_service)
) -> HTMLResponse:
    logger.info('Resume notifications request')
    try:
        email = subscription_service.validate_token(token, 'resume')
        user_language = subscription_service.get_user_language(email)

        subscription_service.update_pause_status(email, False)

        return template_service.render_resume(request, email, language=user_language)
    except InvalidTokenError as e:
        return handle_token_error(e, request, token, 'resume', subscription_service, template_service)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
