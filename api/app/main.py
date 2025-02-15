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


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
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

confirmation_client = EmailClient(
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
    logger.info("Initializing database and Redis connection...")
    init_db()
    await FastAPILimiter.init(redis)
    yield
    logger.info("Shutting down: closing Redis connection...")
    await redis.aclose()


app = FastAPI(
    lifespan=lifespan,
    # dependencies=[Depends(RateLimiter(times=5, minutes=15))]
)
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')


# Middleware to log all incoming requests and their responses
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("Incoming request: %s %s", request.method, request.url)
    response = await call_next(request)
    logger.info("Completed request: %s %s with status %s", request.method, request.url, response.status_code)
    return response


@app.get('/redis-health')
async def redis_health():
    logger.info("Checking Redis health")
    try:
        await redis.ping()
        logger.info("Redis health check passed")
        return {'status': 'ok'}
    except Exception as e:
        logger.error("Redis health check failed: %s", str(e))
        return {'status': 'error', 'detail': str(e)}


@app.get('/')
async def serve_frontend():
    logger.info("Serving frontend index.html")
    return FileResponse('static/index.html')


@app.get('/health')
async def health():
    logger.info("Health check endpoint called")
    return {'status': 'ok'}


@app.post('/subscribe')
async def subscribe(q: str, db: Session = Depends(get_db)):
    logger.info("Subscription request received with query: %s", q)
    try:
        parsed_url = parse_calendar_url(q)
    except InvalidURL as e:
        logger.error("Invalid calendar URL: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as _:
        logger.exception("Unexpected error while parsing calendar URL")
        raise HTTPException(status_code=500, detail='Unexpected error')

    if not is_valid_ical_url(q):
        logger.error("Invalid iCal URL provided: %s", q)
        raise HTTPException(status_code=400, detail='Invalid iCal document at provided URL')

    user = parsed_url['user']
    auth = parsed_url['auth']
    email = f'{user}@{RECIPIENT_DOMAIN}'

    logger.info("Creating subscription for email: %s", email)

    existing = get_subscription(db, email)
    if existing:
        if existing.activated:
            logger.info("Subscription for %s already activated", email)
            raise HTTPException(status_code=400, detail='Subscription already activated')
        else:
            logger.info("Updating calendar auth for existing subscription %s", email)
            existing.calendar_auth = auth
            db.commit()
    else:
        logger.info("Creating new subscription for %s", email)
        create_subscription(db, email, auth)

    try:
        logger.info("Sending activation confirmation email to %s", email)
        confirmation_client.send_activate_confirmation_email(email)
    except Exception as _:
        logger.exception("Error sending activation email to %s", email)
        raise HTTPException(status_code=500, detail='Unexpected error')

    logger.info("Subscription process completed for %s", email)
    return {'status': 'ok', 'email': email}


@app.get('/activate', response_class=HTMLResponse)
async def activate(request: Request, token: str, db: Session = Depends(get_db)):
    logger.info("Activation requested with token: %s", token)
    try:
        email = decode_token(token, 'activate')
        subscription = update_activation(db, email, True)
        if not subscription:
            logger.error("Activation failed: subscription not found for %s", email)
            return templates.TemplateResponse(
                'error.html',
                {
                    'request': request,
                    'title': 'Subscription Not Found',
                    'message': 'We couldn\'t find your subscription',
                    'base_url': API_URL
                }
            )

        logger.info("Subscription activated for %s", email)
        return templates.TemplateResponse(
            'activate.html',
            {
                'request': request,
                'title': 'Account activated',
                'base_url': API_URL,
            }
        )

    except Exception as _:
        logger.exception("Activation failed due to invalid or expired token")
        return templates.TemplateResponse(
            'error.html',
            {
                'request': request,
                'title': 'Invalid Request',
                'message': 'This link is invalid or expired',
                'base_url': API_URL
            }
        )


@app.post('/request-delete')
async def request_delete(email: str, db: Session = Depends(get_db)):
    logger.info("Deletion request received for email: %s", email)
    subscription = get_subscription(db, email)
    if not subscription:
        logger.error("Deletion request failed: subscription not found for %s", email)
        raise HTTPException(status_code=404, detail='Subscription not found')
    try:
        logger.info("Sending deletion confirmation email to %s", email)
        confirmation_client.send_delete_confirmation_email(email)
    except Exception as e:
        logger.exception("Error sending deletion email to %s", email)
        raise HTTPException(status_code=500, detail='Unexpected error while sending deletion email')
    return {'message': 'Deletion confirmation email sent.'}


@app.get('/delete')
async def delete_account(token: str, db: Session = Depends(get_db)):
    logger.info("Delete account requested with token: %s", token)
    try:
        email = decode_token(token, 'delete')
        success = delete_user(db, email)
        if not success:
            logger.error("Delete account failed: account not found or already deleted for %s", email)
            raise HTTPException(status_code=404, detail='Account not found or already deleted.')
        logger.info("Account deleted successfully for %s", email)
        return {'message': 'Account deleted successfully.'}
    except Exception as e:
        logger.exception("Error processing delete account request with token: %s", token)
        raise HTTPException(status_code=500, detail='Unexpected error during account deletion')


@app.post('/request-pause')
async def request_pause(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    logger.info("Pause request received for email: %s", email)
    subscription = get_subscription(db, email)
    if not subscription:
        logger.error("Pause request failed: subscription not found for %s", email)
        return {'message': 'Subscription not found.'}

    if subscription.paused:
        logger.info("Pause request: notifications already paused for %s", email)
        return {'message': 'Email notifications are already paused.'}

    try:
        logger.info("Sending pause confirmation email to %s", email)
        confirmation_client.send_pause_confirmation_email(email)
    except Exception as e:
        logger.exception("Error sending pause confirmation email to %s", email)
        raise HTTPException(status_code=500, detail='Unexpected error while sending pause email')

    return {"message": "Pause confirmation email sent."}


@app.get('/pause', response_class=HTMLResponse)
async def pause_notifications(request: Request, token: str, db: Session = Depends(get_db)):
    logger.info("Pause notifications requested with token: %s", token)
    try:
        email = decode_token(token, "pause")
        subscription = update_paused(db, email, True)
        if not subscription:
            logger.error("Pause notifications failed: subscription not found for %s", email)
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "title": "Subscription Not Found",
                    "message": "We couldn't find your subscription",
                    "base_url": API_URL
                }
            )

        logger.info("Email notifications paused for %s", email)
        return templates.TemplateResponse(
            "pause.html",
            {
                "request": request,
                "email": email,
                "base_url": API_URL
            }
        )

    except Exception as _:
        logger.exception("Error processing pause notifications with token: %s", token)
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Invalid Request",
                "message": "This link is invalid or expired",
                "base_url": API_URL
            }
        )


@app.post('/request-resume')
async def request_resume(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    logger.info("Resume request received for email: %s", email)
    subscription = get_subscription(db, email)
    if not subscription:
        logger.error("Resume request failed: subscription not found for %s", email)
        return {'message': 'Subscription not found.'}

    if not subscription.paused:
        logger.info("Resume request: notifications already active for %s", email)
        return {'message': 'Email notifications are already active.'}

    try:
        logger.info("Sending resume confirmation email to %s", email)
        confirmation_client.send_resume_confirmation_email(email)
    except Exception as e:
        logger.exception("Error sending resume confirmation email to %s", email)
        raise HTTPException(status_code=500, detail='Unexpected error while sending resume email')

    return {"message": "Resume confirmation email sent."}


@app.get('/resume', response_class=HTMLResponse)
async def resume_notifications(request: Request, token: str, db: Session = Depends(get_db)):
    logger.info("Resume notifications requested with token: %s", token)
    try:
        email = decode_token(token, "resume")
        subscription = update_paused(db, email, False)
        if not subscription:
            logger.error("Resume notifications failed: subscription not found for %s", email)
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "title": "Subscription Not Found",
                    "message": "We couldn't find your subscription",
                    "base_url": API_URL
                }
            )

        logger.info("Email notifications resumed for %s", email)
        return templates.TemplateResponse(
            "resume.html",
            {
                "request": request,
                "email": email,
                "base_url": API_URL
            }
        )

    except Exception as _:
        logger.exception("Error processing resume notifications with token: %s", token)
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Invalid Request",
                "message": "This link is invalid or expired",
                "base_url": API_URL
            }
        )


if __name__ == '__main__':
    logger.info("Starting uvicorn server on port %s", API_PORT)
    uvicorn.run(app, port=API_PORT)
