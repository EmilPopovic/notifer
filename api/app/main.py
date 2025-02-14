import os

from pyexpat.errors import messages
from redis import asyncio as aioredis
from contextlib import asynccontextmanager
from http.client import InvalidURL

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Body
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

from api.app.page_templates import confirmation_template, error_template, activation_template

API_PORT = int(os.getenv('API_PORT'))

RECIPIENT_DOMAIN = os.getenv('RECIPIENT_DOMAIN')

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(int(os.getenv('SMTP_PORT')))
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
    init_db()
    await FastAPILimiter.init(redis)
    yield
    await redis.aclose()


app = FastAPI(
    lifespan=lifespan, 
#    dependencies=[Depends(RateLimiter(times=5, minutes=15))]
)
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')


@app.get('/redis-health')
async def redis_health():
    try:
        await redis.ping()
        return {'status': 'ok'}
    except Exception as e:
        return {'status': 'error', 'detail': str(e)}


@app.get('/')
async def serve_frontend():
    return FileResponse('static/index.html')


@app.get('/health')
async def health():
    return {'status': 'ok'}


@app.post('/subscribe')
async def subscribe(q: str, db: Session = Depends(get_db)):
    try:
        parsed_url = parse_calendar_url(q)
    except InvalidURL as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as _:
        raise HTTPException(status_code=500, detail='Unexpected error')
    
    if not is_valid_ical_url(q):
        raise HTTPException(status_code=400, detail='Invalid iCal document at provided URL')
        
    user = parsed_url['user']
    auth = parsed_url['auth']
    email = f'{user}@{RECIPIENT_DOMAIN}'
    
    print('creating subscription')
    
    existing = get_subscription(db, email)
    if existing:
        if existing.activated:
            raise HTTPException(status_code=400, detail='Subscription already activated')
        else:
            existing.calendar_auth = auth
            db.commit()
    else:
        create_subscription(db, email, auth)
    
    try:
        confirmation_client.send_activate_confirmation_email(email)
    except Exception as _:
        raise HTTPException(status_code=500, detail='Unexpected error')
    
    return {'status': 'ok', 'email': email}


@app.get('/activate', response_class=HTMLResponse)
async def activate(token: str, db: Session = Depends(get_db)):
    try:
        email = decode_token(token, 'activate')
        subscription = update_activation(db, email, True)
        if not subscription:
            return HTMLResponse(
                error_template.format(
                    emoji='🦄',
                    messages='It should not be possible to reach this error. Congrats! You will probably need to sign up again.',
                    base_url=API_URL
                ),
                status_code=404
            )
        
        return templates.TemplateResponse(
            'activate.html',
            {
                'request': None,
                'title': 'Account activated',
                'base_url': API_URL,
            }
        )
    
    except Exception as _:
        return HTMLResponse(
            error_template.format(
                emoji='⚠️',
                message='Invalid or expired token',
                base_url=API_URL
            ),
            status_code=400
        )


@app.post('/request-delete')
async def request_delete(email: str, db: Session = Depends(get_db)):
    subscription = get_subscription(db, email)
    if not subscription:
        raise HTTPException(status_code=404, detail='Subscription not found')
    confirmation_client.send_delete_confirmation_email(email)
    return {'message': 'Deletion confirmation email sent.'}


@app.get('/delete')
async def delete_account(token: str, db: Session = Depends(get_db)):
    email = decode_token(token, 'delete')
    success = delete_user(db, email)
    if not success:
        raise HTTPException(status_code=404, detail='Account not found or already deleted.')
    return {'message': 'Account deleted successfully.'}


@app.post('/request-pause')
async def request_pause(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    subscription = get_subscription(db, email)
    if not subscription:
        return {'message': 'Subscription not found.'}
    
    if subscription.paused:
        return {'message': 'Email notifications are already paused.'}
        
    confirmation_client.send_pause_confirmation_email(email)
    return {"message": "Pause confirmation email sent."}


@app.get('/pause', response_class=HTMLResponse)
async def pause_notifications(token: str, db: Session = Depends(get_db)):
    try:
        email = decode_token(token, "pause")
        subscription = update_paused(db, email, True)
        if not subscription:
            return HTMLResponse(
                error_template.format(
                    emoji='🦄',
                    messages='It should not be possible to reach this error. Congrats! You will probably need to sign up again.',
                    base_url=API_URL
                ),
                status_code=404
            )
        
        return HTMLResponse(
            confirmation_template.format(
                emoji='⏸️',
                title='Notifications Paused',
                message='You will no loger receive change notifications for your calendar.',
                base_url=API_URL
            )
        )
    
    except Exception as _:
        return HTMLResponse(
            error_template.format(
                emoji='⚠️',
                message='Invalid or expired token',
                base_url=API_URL
            ),
            status_code=400
        )


@app.post('/request-resume')
async def request_resume(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    subscription = get_subscription(db, email)
    if not subscription:
        return {'message': 'Subscription not found.'}
    
    if not subscription.paused:
        return {'message': 'Email notifications are already active.'}
    
    confirmation_client.send_resume_confirmation_email(email)
    return {"message": "Resume confirmation email sent."}


@app.get('/resume')
async def resume_notifications(token: str, db: Session = Depends(get_db)):
    try:
        email = decode_token(token, "resume")
        subscription = update_paused(db, email, False)
        if not subscription:
            return HTMLResponse(
                error_template.format(
                    emoji='🦄',
                    messages='It should not be possible to reach this error. Congrats! You will probably need to sign up again.',
                    base_url=API_URL
                ),
                status_code=404
            )
        
        return HTMLResponse(
            confirmation_template.format(
                emoji='▶️',
                title='Notifications Resumed',
                message='You will now receive change notifications for your calendar.',
                base_url=API_URL
            )
        )
    
    except Exception as _:
        return HTMLResponse(
            error_template.format(
                emoji='⚠️',
                message='Invalid or expired token',
                base_url=API_URL
            ),
            status_code=400
        )


if __name__ == '__main__':
    uvicorn.run(app, port=API_PORT)
