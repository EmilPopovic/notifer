import logging
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from shared.database import get_db
from shared.crud import (
    get_all_subscriptions,
    get_subscription,
    get_audit_logs,
    get_audit_log_count,
    get_audit_logs_for_email,
    update_paused,
    delete_user as crud_delete_user,
    create_audit_log,
)
from shared.auth_utils import (
    COOKIE_NAME,
    _SESSION_HOURS,
    verify_password,
    create_session_token,
    verify_session_token,
)
from shared.token_utils import JWT_KEY
from config import get_settings
from api.dependencies import get_templates

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/dashboard', tags=['dashboard'])

_PER_PAGE = 50
_ACTION_TYPES = [
    'subscription_created',
    'subscription_resubmit',
    'subscription_activated',
    'subscription_paused',
    'subscription_resumed',
    'subscription_deleted',
    'email_queued',
    'notification_queued',
]


def _is_authenticated(request: Request) -> bool:
    token = request.cookies.get(COOKIE_NAME)
    return verify_session_token(token, JWT_KEY) if token else False


def _login_redirect() -> RedirectResponse:
    return RedirectResponse('/dashboard/login', status_code=302)


@router.get('/login', response_class=HTMLResponse)
async def login_page(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
):
    if _is_authenticated(request):
        return RedirectResponse('/dashboard/', status_code=302)
    return templates.TemplateResponse('dashboard/login.html', {'request': request})


@router.post('/login')
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    templates: Jinja2Templates = Depends(get_templates),
):
    settings = get_settings()
    if (
        username == settings.dashboard_username
        and verify_password(password, settings.dashboard_password_hash)
    ):
        response = RedirectResponse('/dashboard/', status_code=302)
        response.set_cookie(
            COOKIE_NAME,
            create_session_token(JWT_KEY),
            httponly=True,
            samesite='strict',
            max_age=_SESSION_HOURS * 3600,
        )
        return response
    return templates.TemplateResponse(
        'dashboard/login.html',
        {'request': request, 'error': 'Invalid credentials'},
        status_code=401,
    )


@router.post('/logout')
async def logout():
    response = RedirectResponse('/dashboard/login', status_code=302)
    response.delete_cookie(COOKIE_NAME)
    return response


@router.get('/', response_class=HTMLResponse)
async def dashboard_index(
    request: Request,
    page: int = 1,
    email_filter: str = '',
    action_filter: str = '',
    db: Session = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
):
    if not _is_authenticated(request):
        return _login_redirect()

    subscriptions = get_all_subscriptions(db)

    ef = email_filter.strip() or None
    af = action_filter.strip() or None
    total_logs = get_audit_log_count(db, email=ef, action=af)
    logs = get_audit_logs(db, page=page, per_page=_PER_PAGE, email=ef, action=af)
    total_pages = max(1, (total_logs + _PER_PAGE - 1) // _PER_PAGE)

    stats = {
        'total': len(subscriptions),
        'active': sum(1 for s in subscriptions if s.activated and not s.paused),
        'paused': sum(1 for s in subscriptions if s.activated and s.paused),
        'pending': sum(1 for s in subscriptions if not s.activated),
    }

    return templates.TemplateResponse('dashboard/index.html', {
        'request': request,
        'subscriptions': subscriptions,
        'logs': logs,
        'total_logs': total_logs,
        'page': page,
        'total_pages': total_pages,
        'email_filter': email_filter,
        'action_filter': action_filter,
        'stats': stats,
        'action_types': _ACTION_TYPES,
    })


@router.get('/user', response_class=HTMLResponse)
async def user_detail(
    request: Request,
    email: str,
    db: Session = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
):
    if not _is_authenticated(request):
        return _login_redirect()

    sub = get_subscription(db, email)
    if not sub:
        return RedirectResponse('/dashboard/', status_code=302)

    logs = get_audit_logs_for_email(db, email)

    return templates.TemplateResponse('dashboard/user.html', {
        'request': request,
        'sub': sub,
        'logs': logs,
    })


@router.post('/action')
async def perform_action(
    request: Request,
    email: str = Form(...),
    action: str = Form(...),
    next_url: str = Form('/dashboard/'),
    db: Session = Depends(get_db),
):
    if not _is_authenticated(request):
        return _login_redirect()

    if not next_url.startswith('/dashboard'):
        next_url = '/dashboard/'

    if action == 'pause':
        create_audit_log(db, 'subscription_paused', email, details='admin_dashboard')
        update_paused(db, email, True)
    elif action == 'unpause':
        create_audit_log(db, 'subscription_resumed', email, details='admin_dashboard')
        update_paused(db, email, False)
    elif action == 'delete':
        create_audit_log(db, 'subscription_deleted', email, details='admin_dashboard')
        crud_delete_user(db, email)
        next_url = '/dashboard/'

    return RedirectResponse(next_url, status_code=302)
