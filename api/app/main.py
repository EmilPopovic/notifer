import os
import logging
from redis import asyncio as aioredis
from contextlib import asynccontextmanager
from http.client import InvalidURL

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Body, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse

from shared.calendar_utils import parse_calendar_url, is_valid_ical_url
from shared.database import init_db, get_db
from shared.crud import (
    create_subscription,
    get_subscription,
    update_activation,
    delete_user,
    update_paused,
)
from shared.email_utils import EmailClient
from shared.token_utils import decode_token
from shared.secrets import get_secret
from shared.emoji_utils import emojify


# region setup


LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | "
    "%(funcName)s() | %(threadName)s | %(message)s"
)

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

API_PORT = int(os.getenv('API_PORT', 8000))
RECIPIENT_DOMAIN = 'fer.hr'

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
CONFIRMATION_USERNAME = os.getenv('CONFIRMATION_USERNAME')
RESEND_API_KEY = get_secret('RESEND_API_KEY_FILE')
CONFIRMATION_FALLBACK_USERNAME = os.getenv('CONFIRMATION_FALLBACK_USERNAME')
CONFIRMATION_PASSWORD = get_secret('CONFIRMATION_PASSWORD_FILE')
FROM_EMAIL = CONFIRMATION_FALLBACK_USERNAME
API_URL = os.getenv('API_URL').replace('${API_PORT}', str(API_PORT))

email_client = EmailClient(
    resend_from_email=CONFIRMATION_USERNAME,
    resend_api_key=RESEND_API_KEY,
    fallback_smtp_server=SMTP_SERVER,
    fallback_smtp_port=SMTP_PORT,
    fallback_username=CONFIRMATION_FALLBACK_USERNAME,
    fallback_password=CONFIRMATION_PASSWORD,
    fallback_from_email=FROM_EMAIL,
    api_base_url=API_URL
)

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
redis = aioredis.from_url(REDIS_URL)


async def rate_limit_exceeded_callback(request:Request, _, pexpire: int):
    logger.warning(f'Rate limit exceeded for client {request.client.host} on endpoint {request.url.path}')
    
    raise HTTPException(
        status_code=429,
        detail=f'⏳ Previše zahtjeva. Pokušaj ponovno za {pexpire // 1000 // 60} minuta.',
        headers={'Retry-After': str(pexpire)}
    )

GLOBAL_RATE_LIMIT = 15
GLOBAL_RATE_LIMIT_MINUTES = 15

global_limiter = RateLimiter(
    times=GLOBAL_RATE_LIMIT,
    minutes=GLOBAL_RATE_LIMIT_MINUTES,
    callback=rate_limit_exceeded_callback
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info('Initializing database and Redis connection...')
    init_db()
    logger.info('Database initialized. Starting Redis...')
    
    await FastAPILimiter.init(redis)
    
    yield
    
    logger.info('Shutting down: closing Redis connection...')
    await redis.aclose()


app = FastAPI(lifespan=lifespan)
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[API_URL],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


# endregion
# region utility endpoints


@app.middleware('http')
async def log_requests(request: Request, call_next):
    forwarded_for = request.headers.get('X-Forwarded-For')
    client_ip = forwarded_for.split(',')[0] if forwarded_for else request.client.host
    logger.info(f'Incoming request from {client_ip}: {request.method} {request.url}')
    response = await call_next(request)
    logger.info(f'Completed request: {request.method} {request.url} with status {response.status_code}')
    return response


@app.get('/redis-health')
async def redis_health():
    logger.info('Checking Redis health')
    try:
        await redis.ping()
        logger.info('Redis health check passed')
        return {'status': 'ok'}
    except Exception as e:
        logger.error(f'Redis health check failed: str(e)')
        return {'status': 'error', 'detail': str(e)}


@app.get('/')
async def serve_frontend():
    logger.info('Serving frontend index.html')
    return FileResponse('static/index.html')


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    logger.info('Serving favicon')
    return FileResponse('api/app/favicon.ico')


@app.get('/health')
async def health():
    logger.info('Health check endpoint called')
    return {'status': 'ok'}


# endregion
# region user endpoints

@app.post('/subscribe', dependencies=[Depends(global_limiter)])
async def subscribe(q: str, db: Session = Depends(get_db)):
    logger.info(f'Subscription request received with query: {q}')
    try:
        parsed_url = parse_calendar_url(q)
    except InvalidURL as e:
        logger.error(f'Invalid calendar URL: {str(e)}')
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f'Unexpected error while parsing calendar URL: {str(e)}')
        raise HTTPException(status_code=500, detail='🔧 Neočekivana greška.')

    if not is_valid_ical_url(q):
        logger.error(f'Invalid iCal URL provided: {q}')
        raise HTTPException(status_code=400, detail='❌ Na URL-u nije valjan iCal dokument.')

    user = parsed_url['user']
    auth = parsed_url['auth']
    email = f'{user}@{RECIPIENT_DOMAIN}'

    logger.info(f'Creating subscription for email: {email}')

    existing = get_subscription(db, email)
    if existing:
        if existing.activated:
            logger.info(f'Subscription for {email} already activated')
            raise HTTPException(status_code=400, detail='🪄 Pretplata već aktivirana.')
        else:
            logger.info(f'Updating calendar auth for existing subscription {email}')
            existing.calendar_auth = auth
            db.commit()
    else:
        logger.info(f'Creating new subscription for {email}')
        create_subscription(db, email, auth)

    logger.info(f'Enqueuing activation confirmation email to {email}')
    email_client.enqueue_send_activate_confirmation_email(email)

    logger.info(f'Subscription process completed for {email}')
    return {'status': 'ok', 'email': email}


@app.get('/activate', response_class=HTMLResponse)
async def activate(request: Request, token: str, db: Session = Depends(get_db)):
    logger.info(f'Activation requested with token: {token}')
    try:
        email = decode_token(token, 'activate')
        subscription = update_activation(db, email, True)
        if not subscription:
            logger.error(f'Activation failed: subscription not found for {email}')
            response = templates.TemplateResponse(
                'error.html',
                {
                    'request': request,
                    'title': 'Pretplata nije pronađena',
                    'message': 'Nismo uspjeli pronaći tvoju pretplatu.',
                    'base_url': API_URL
                }
            )
            return emojify(response)

        logger.info(f'Subscription activated for {email}')
        response = templates.TemplateResponse(
            'activate.html',
            {
                'request': request,
                'title': 'Pretplata aktivirana',
                'base_url': API_URL,
            }
        )
        return emojify(response)

    except Exception as _:
        logger.exception('Activation failed due to invalid or expired token')
        response = templates.TemplateResponse(
            'error.html',
            {
                'request': request,
                'title': 'Greška',
                'message': 'Ovaj link nije valjan ili je istekao.',
                'base_url': API_URL
            }
        )
        return emojify(response)


@app.post('/request-delete', dependencies=[Depends(global_limiter)])
async def request_delete(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    logger.info(f'Deletion request received for email: {email}')
    subscription = get_subscription(db, email)
    if not subscription:
        logger.error(f'Deletion request failed: subscription not found for {email}')
        raise HTTPException(status_code=404, detail='🗃️ Pretplata nije pronađena.')
    
    logger.info(f'Enqueuing deletion confirmation email to {email}')
    email_client.enqueue_send_delete_confirmation_email(email)
    
    return {'message': 'Deletion confirmation email sent.'}


@app.get('/delete')
async def delete_account(request: Request, token: str, db: Session = Depends(get_db)):
    logger.info(f'Delete account requested with token: {token}')
    try:
        email = decode_token(token, 'delete')
        success = delete_user(db, email)
        if not success:
            logger.error(f'Delete account failed: account not found or already deleted for {email}')
            response = templates.TemplateResponse(
                'error.html',
                {
                    'request': request,
                    'title': 'Pretplata nije pronađena',
                    'message': 'Pretplata nije pronađena ili je već izbrisana.',
                    'base_url': API_URL
                }
            )
            return emojify(response)
        
        logger.info(f'Account deleted successfully for {email}')
        response = templates.TemplateResponse(
            'delete.html',
            {
                'title': 'Račun izbrisan',
                'request': request,
                'email': email,
                'base_url': API_URL
            }
        )
        return emojify(response)
    
    except Exception as _:
        logger.exception(f'Error processing delete account request with token: {token}')
        response = templates.TemplateResponse(
            'error.html',
            {
                'request': request,
                'title': 'Greška',
                'message': 'Ovaj link nije valjan ili je zastario.',
                'base_url': API_URL
            }
        )
        return emojify(response)


@app.post('/request-pause', dependencies=[Depends(global_limiter)])
async def request_pause(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    logger.info(f'Pause request received for email: {email}')
    subscription = get_subscription(db, email)
    if not subscription or not subscription.activated:
        logger.error(f'Pause request failed: subscription not found for {email}')
        raise HTTPException(status_code=404, detail='🗃️ Pretplata nije pronađena.')

    if subscription.paused:
        logger.info(f'Pause request: notifications already paused for {email}')
        raise HTTPException(status_code=400, detail='🪄 Obavijesti su već pauzirane.')

    logger.info(f'Enqueuing pause confirmation email to {email}')
    email_client.enqueue_send_pause_confirmation_email(email)

    return {'message': 'Pause confirmation email sent.'}


@app.get('/pause', response_class=HTMLResponse)
async def pause_notifications(request: Request, token: str, db: Session = Depends(get_db)):
    logger.info(f'Pause notifications requested with token: {token}')
    try:
        email = decode_token(token, 'pause')
        subscription = update_paused(db, email, True)
        if not subscription:
            logger.error(f'Pause notifications failed: subscription not found for {email}')
            response = templates.TemplateResponse(
                'error.html',
                {
                    'request': request,
                    'title': 'Pretplata nije pronađenja',
                    'message': 'Nismo uspjeli pronaći tvoju pretplatu.',
                    'base_url': API_URL
                }
            )
            return emojify(response)

        logger.info(f'Email notifications paused for {email}')
        response = templates.TemplateResponse(
            'pause.html',
            {
                'title': 'Obavijesti pauzirane',
                'request': request,
                'email': email,
                'base_url': API_URL
            }
        )
        return emojify(response)

    except Exception as _:
        logger.exception(f'Error processing pause notifications with token: {token}')
        response = templates.TemplateResponse(
            'error.html',
            {
                'request': request,
                'title': 'Greška',
                'message': 'Ovaj link nije valjan ili je zastario.',
                'base_url': API_URL
            }
        )
        return emojify(response)


@app.post('/request-resume', dependencies=[Depends(global_limiter)])
async def request_resume(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    logger.info(f'Resume request received for email: {email}')
    subscription = get_subscription(db, email)
    if not subscription or not subscription.activated:
        logger.error(f'Resume request failed: subscription not found for {email}')
        raise HTTPException(status_code=404, detail='🗃️ Pretplata nije pronađena.')

    if not subscription.paused:
        logger.info(f'Resume request: notifications already active for {email}')
        raise HTTPException(status_code=400, detail='🪄 Obavijesti su već aktivne.')

    logger.info(f'Enqueuing resume confirmation email to {email}')
    email_client.enqueue_send_resume_confirmation_email(email)

    return {'message': 'Resume confirmation email sent.'}


@app.get('/resume', response_class=HTMLResponse)
async def resume_notifications(request: Request, token: str, db: Session = Depends(get_db)):
    logger.info(f'Resume notifications requested with token: {token}')
    try:
        email = decode_token(token, 'resume')
        subscription = update_paused(db, email, False)
        if not subscription:
            logger.error(f'Resume notifications failed: subscription not found for {email}')
            response = templates.TemplateResponse(
                'error.html',
                {
                    'request': request,
                    'title': 'Pretplata nije pronađena',
                    'message': 'Nismo uspjeli pronaći tvoju pretplatu.',
                    'base_url': API_URL
                }
            )
            return emojify(response)

        logger.info(f'Email notifications resumed for {email}')
        response = templates.TemplateResponse(
            'resume.html',
            {
                'title': 'Uključene obavijesti',
                'request': request,
                'email': email,
                'base_url': API_URL
            }
        )
        return emojify(response)

    except Exception as _:
        logger.exception(f'Error processing resume notifications with token: {token}')
        response = templates.TemplateResponse(
            'error.html',
            {
                'request': request,
                'title': 'Greška',
                'message': 'Ovaj link nije valjan ili je zastario.',
                'base_url': API_URL
            }
        )
        return emojify(response)


# endregion


if __name__ == '__main__':
    logger.info(f'Starting uvicorn server on port {API_PORT}')
    logger.info(f'Application url is {API_URL}')
    uvicorn.run(app, host='0.0.0.0', port=API_PORT)
