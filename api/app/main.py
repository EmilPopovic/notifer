import logging
import redis
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

from shared.database import init_db
from .config import get_settings
from .routers import health, subscriptions, frontend
from .middleware import log_request_middleware
from .dependencies import get_redis_client

# Setup logging
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

settings = get_settings()

# HTTP Request Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests currently being processed'
)

# Custom Prometheus metrics
active_subscriptions_gauge = Gauge(
    'notifer_active_subscriptions_total',
    'Number of active subscriptions'
)

total_subscriptions_gauge = Gauge(
    'notifer_total_subscriptions',
    'Total number of subscriptions'
)

email_queue_size_gauge = Gauge(
    'notifer_email_queue_size',
    'Number of emails in queue'
)

class HTTPMetricsMiddleware(BaseHTTPMiddleware):
    '''Middleware to track HTTP request metrics.'''

    async def dispatch(self, request: Request, call_next):
        # Start timing and increment in-progress counter
        start_time = time.time()
        http_requests_in_progress.inc()

        try:
            # Process the request
            response = await call_next(request)

            # Calculate metrics
            duration = time.time() - start_time
            method = request.method
            endpoint = self._get_endpoint_path(request)
            status_code = str(response.status_code)

            # Record metrics
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            return response
        
        except Exception as _:
            # Handle errors and still record metrics
            duration = time.time() - start_time
            method = request.method
            endpoint = self._get_endpoint_path(request)

            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code='500'
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            raise

        finally:
            # Decrement the in-progress counter
            http_requests_in_progress.dec()

    def _get_endpoint_path(self, request: Request) -> str:
        '''Extract the endpoint path template for consistent labeling.'''
        if hasattr(request, 'scope') and 'route' in request.scope:
            route = request.scope['route']
            if hasattr(route, 'path'):
                return route.path
        # Fallback to actual path
        return request.url.path

@asynccontextmanager
async def lifespan(_: FastAPI):
    '''Application lifespan management.'''
    # Print all registered routes
    for route in app.routes:
        if hasattr(route, 'path'):
            logger.info(f'Route: {route.path} | Methods: {getattr(route, 'methods', 'N/A')}')  # pyright: ignore[reportAttributeAccessIssue]

    # Startup
    logger.info('Starting Redis connection...')
    redis_client = await get_redis_client()
    await FastAPILimiter.init(redis_client)

    logger.info('Application started successfully')

    yield

    # Shutdown
    logger.info('Shutting down: closing Redis connection...')
    await redis_client.close()
    logger.info('Application shutdown complete')

def update_custom_metrics():
    try:
        from shared.database import SessionLocal
        from shared.models import UserCalendar

        session = SessionLocal()
        try:
            active_count = session.query(UserCalendar).filter(
                UserCalendar.activated.is_(True),
                UserCalendar.paused.is_(False)
            ).count()
            active_subscriptions_gauge.set(active_count)

            total_count = session.query(UserCalendar).count()
            total_subscriptions_gauge.set(total_count)
        finally:
            session.close()

        r = redis.Redis.from_url(settings.redis_url)
        queue_size = r.llen('rq:queue:email')
        email_queue_size_gauge.set(queue_size) # pyright: ignore[reportArgumentType]
    
    except Exception as e:
        logger.error(f'Error updating custom metrics: {e}')

def create_app() -> FastAPI:
    app = FastAPI(
        title='NotiFER',
        description='A web application allowing students of FER Zagreb to subscribe to email notifications about timetable chagnes.',
        version='2.0.2',
        lifespan=lifespan
    )

    app.add_middleware(HTTPMetricsMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.middleware('http')(log_request_middleware)

    @app.get('/metrics')
    async def metrics():
        update_custom_metrics()
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    # Include routers
    app.include_router(health.router)
    app.include_router(subscriptions.router)
    app.include_router(frontend.router)

    # Mount static files
    app.mount('/static', StaticFiles(directory='static'), name='static')

    return app

def start_server():
    '''Start the uvicorn server.'''
    logger.info('Initializing database...')
    init_db()
    logger.info('Database initialized')

    logger.info(f'Starting uvicorn server on port {settings.api_port}')
    logger.info(f'Application URL: {settings.api_url}')

    uvicorn.run(
        'app.main:app',
        host='0.0.0.0',
        port=settings.api_port,
        reload=False,
        access_log=True
    )

app = create_app()

if __name__ == '__main__':
    start_server()
