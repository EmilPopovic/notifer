from fastapi import Request, HTTPException
from fastapi_throttle import RateLimiter
import logging
from config import get_settings

logger = logging.getLogger(__name__)

async def rate_limit_exceeded_callback(request: Request, response, pexpire: int):
    '''Callback for when rate limit is exceeded.'''
    host = '<unknown_client>' if request.client is None else request.client.host
    logger.warning(f'Rate limit exceeded for client {host} on endpoint {request.url.path}')
    
    raise HTTPException(
        status_code=429,
        detail=f'Too many requests. Try again in {pexpire // 1000 // 60} minutes.',
        headers={'Retry-After': str(pexpire)}
    )

async def log_request_middleware(request: Request, call_next):
    '''Log incoming requests and responses.'''
    forwarded_for = request.headers.get('X-Forwarded-For')
    host = '<unknown_client>' if request.client is None else request.client.host
    client_ip = forwarded_for.split(',')[0] if forwarded_for else host
    logger.info(f'Incoming request from {client_ip}: {request.method} {request.url}')
    
    response = await call_next(request)
    
    logger.info(f'Completed request: {request.method} {request.url} with status {response.status_code}')
    return response

def get_rate_limiter():
    '''Get configured rate limiter.'''
    settings = get_settings()
    return RateLimiter(
        times=settings.global_rate_limit,
        seconds=settings.global_rate_limit_minutes * 60
    )
