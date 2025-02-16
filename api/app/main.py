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


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

API_PORT = int(os.getenv('API_PORT'))
RECIPIENT_DOMAIN = os.getenv('RECIPIENT_DOMAIN')

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
CONFIRMATION_USERNAME = os.getenv('CONFIRMATION_USERNAME')
CONFIRMATION_PASSWORD = os.getenv('CONFIRMATION_PASSWORD')
FROM_EMAIL = CONFIRMATION_USERNAME
API_URL = os.getenv('API_URL').replace('${API_PORT}', str(API_PORT))
RATE_LIMIT = int(os.getenv('RATE_LIMIT', 5))

email_client = EmailClient(
    smtp_server=SMTP_SERVER,
    smtp_port=SMTP_PORT,
    username=CONFIRMATION_USERNAME,
    password=CONFIRMATION_PASSWORD,
    from_email=FROM_EMAIL,
    base_url=API_URL
)

REDIS_URL = os.getenv('REDIS_URL')
redis = aioredis.from_url(REDIS_URL)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info('Initializing database and Redis connection...')
    init_db()
    await FastAPILimiter.init(redis)
    yield
    logger.info('Shutting down: closing Redis connection...')
    await redis.aclose()


app = FastAPI(lifespan=lifespan)
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

#app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[API_URL],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.middleware('http')
async def log_requests(request: Request, call_next):
    logger.info('Incoming request: %s %s', request.method, request.url)
    response = await call_next(request)
    logger.info('Completed request: %s %s with status %s', request.method, request.url, response.status_code)
    return response


@app.get('/redis-health')
async def redis_health():
    logger.info('Checking Redis health')
    try:
        await redis.ping()
        logger.info('Redis health check passed')
        return {'status': 'ok'}
    except Exception as e:
        logger.error('Redis health check failed: %s', str(e))
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


@app.post('/subscribe', dependencies=[Depends(RateLimiter(times=RATE_LIMIT, minutes=15))])
async def subscribe(q: str, db: Session = Depends(get_db)):
    logger.info('Subscription request received with query: %s', q)
    try:
        parsed_url = parse_calendar_url(q)
    except InvalidURL as e:
        logger.error('❌ Invalid calendar URL: %s', str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as _:
        logger.exception('Unexpected error while parsing calendar URL')
        raise HTTPException(status_code=500, detail='🔧 Neočekivana greška.')

    if not is_valid_ical_url(q):
        logger.error('Invalid iCal URL provided: %s', q)
        raise HTTPException(status_code=400, detail='❌ Na URL-u nije valjan iCal dokument.')

    user = parsed_url['user']
    auth = parsed_url['auth']
    email = f'{user}@{RECIPIENT_DOMAIN}'

    logger.info('Creating subscription for email: %s', email)

    existing = get_subscription(db, email)
    if existing:
        if existing.activated:
            logger.info('Subscription for %s already activated', email)
            raise HTTPException(status_code=400, detail='Pretplata već aktivirana.')
        else:
            logger.info('Updating calendar auth for existing subscription %s', email)
            existing.calendar_auth = auth
            db.commit()
    else:
        logger.info('Creating new subscription for %s', email)
        create_subscription(db, email, auth)

    logger.info('Enqueuing activation confirmation email to %s', email)
    email_client.enqueue_send_activate_confirmation_email(email)

    logger.info('Subscription process completed for %s', email)
    return {'status': 'ok', 'email': email}


@app.get('/activate', response_class=HTMLResponse)
async def activate(request: Request, token: str, db: Session = Depends(get_db)):
    logger.info('Activation requested with token: %s', token)
    try:
        email = decode_token(token, 'activate')
        subscription = update_activation(db, email, True)
        if not subscription:
            logger.error('Activation failed: subscription not found for %s', email)
            return templates.TemplateResponse(
                'error.html',
                {
                    'request': request,
                    'title': 'Pretplata nije pronađena',
                    'message': 'Nismo uspjeli pronaći tvoju pretplatu.',
                    'base_url': API_URL
                }
            )

        logger.info('Subscription activated for %s', email)
        return templates.TemplateResponse(
            'activate.html',
            {
                'request': request,
                'title': 'Pretplata aktivirana',
                'base_url': API_URL,
            }
        )

    except Exception as _:
        logger.exception('Activation failed due to invalid or expired token')
        return templates.TemplateResponse(
            'error.html',
            {
                'request': request,
                'title': 'Greška',
                'message': 'Ovaj link nije valjan ili je istekao.',
                'base_url': API_URL
            }
        )


@app.post('/request-delete', dependencies=[Depends(RateLimiter(times=RATE_LIMIT, minutes=15))])
async def request_delete(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    logger.info('Deletion request received for email: %s', email)
    subscription = get_subscription(db, email)
    if not subscription:
        logger.error('Deletion request failed: subscription not found for %s', email)
        raise HTTPException(status_code=404, detail='Pretplata nije pronađena.')
    
    logger.info('Enqueuing deletion confirmation email to %s', email)
    email_client.enqueue_send_delete_confirmation_email(email)
    
    return {'message': 'Deletion confirmation email sent.'}


@app.get('/delete')
async def delete_account(request: Request, token: str, db: Session = Depends(get_db)):
    logger.info('Delete account requested with token: %s', token)
    try:
        email = decode_token(token, 'delete')
        success = delete_user(db, email)
        if not success:
            logger.error('Delete account failed: account not found or already deleted for %s', email)
            return templates.TemplateResponse(
                'error.html',
                {
                    'request': request,
                    'title': 'Pretplata nije pronađena',
                    'message': 'Pretplata nije pronađena ili je već izbrisana.',
                    'base_url': API_URL
                }
            )
        
        logger.info('Account deleted successfully for %s', email)
        return templates.TemplateResponse(
            'delete.html',
            {
                'title': 'Račun izbrisan',
                'request': request,
                'email': email,
                'base_url': API_URL
            }
        )
    
    except Exception as _:
        logger.exception('Error processing delete account request with token: %s', token)
        return templates.TemplateResponse(
            'error.html',
            {
                'request': request,
                'title': 'Greška',
                'message': 'Ovaj link nije valjan ili je zastario.',
                'base_url': API_URL
            }
        )


@app.post('/request-pause', dependencies=[Depends(RateLimiter(times=RATE_LIMIT, minutes=15))])
async def request_pause(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    logger.info('Pause request received for email: %s', email)
    subscription = get_subscription(db, email)
    if not subscription or not subscription.activated:
        logger.error('Pause request failed: subscription not found for %s', email)
        raise HTTPException(status_code=404, detail='Pretplata nije pronađena.')

    if subscription.paused:
        logger.info('Pause request: notifications already paused for %s', email)
        raise HTTPException(status_code=400, detail='Obavijesti su već pauzirane.')

    logger.info('Enqueuing pause confirmation email to %s', email)
    email_client.enqueue_send_pause_confirmation_email(email)

    return {'message': 'Pause confirmation email sent.'}


@app.get('/pause', response_class=HTMLResponse)
async def pause_notifications(request: Request, token: str, db: Session = Depends(get_db)):
    logger.info('Pause notifications requested with token: %s', token)
    try:
        email = decode_token(token, 'pause')
        subscription = update_paused(db, email, True)
        if not subscription:
            logger.error('Pause notifications failed: subscription not found for %s', email)
            return templates.TemplateResponse(
                'error.html',
                {
                    'request': request,
                    'title': 'Pretplata nije pronađenja',
                    'message': 'Nismo uspjeli pronaći tvoju pretplatu.',
                    'base_url': API_URL
                }
            )

        logger.info('Email notifications paused for %s', email)
        return templates.TemplateResponse(
            'pause.html',
            {
                'title': 'Obavijesti pauzirane',
                'request': request,
                'email': email,
                'base_url': API_URL
            }
        )

    except Exception as _:
        logger.exception('Error processing pause notifications with token: %s', token)
        return templates.TemplateResponse(
            'error.html',
            {
                'request': request,
                'title': 'Greška',
                'message': 'Ovaj link nije valjan ili je zastario.',
                'base_url': API_URL
            }
        )


@app.post('/request-resume', dependencies=[Depends(RateLimiter(times=RATE_LIMIT, minutes=15))])
async def request_resume(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    logger.info('Resume request received for email: %s', email)
    subscription = get_subscription(db, email)
    if not subscription or not subscription.activated:
        logger.error('Resume request failed: subscription not found for %s', email)
        raise HTTPException(status_code=404, detail='Pretplata nije pronađena.')

    if not subscription.paused:
        logger.info('Resume request: notifications already active for %s', email)
        raise HTTPException(status_code=400, detail='Obavijesti su već aktivne.')

    logger.info('Enqueuing resume confirmation email to %s', email)
    email_client.enqueue_send_resume_confirmation_email(email)

    return {'message': 'Resume confirmation email sent.'}


@app.get('/resume', response_class=HTMLResponse)
async def resume_notifications(request: Request, token: str, db: Session = Depends(get_db)):
    logger.info('Resume notifications requested with token: %s', token)
    try:
        email = decode_token(token, 'resume')
        subscription = update_paused(db, email, False)
        if not subscription:
            logger.error('Resume notifications failed: subscription not found for %s', email)
            return templates.TemplateResponse(
                'error.html',
                {
                    'request': request,
                    'title': 'Pretplata nije pronađena',
                    'message': 'Nismo uspjeli pronaći tvoju pretplatu.',
                    'base_url': API_URL
                }
            )

        logger.info('Email notifications resumed for %s', email)
        return templates.TemplateResponse(
            'resume.html',
            {
                'title': 'Uključene obavijesti',
                'request': request,
                'email': email,
                'base_url': API_URL
            }
        )

    except Exception as _:
        logger.exception('Error processing resume notifications with token: %s', token)
        return templates.TemplateResponse(
            'error.html',
            {
                'request': request,
                'title': 'Greška',
                'message': 'Ovaj link nije valjan ili je zastario.',
                'base_url': API_URL
            }
        )


if __name__ == '__main__':
    logger.info('Starting uvicorn server on port %s', API_PORT)
    logger.info('Application url is %s', API_URL)
    uvicorn.run(app, host='0.0.0.0', port=API_PORT)
