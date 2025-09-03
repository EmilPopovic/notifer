import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .routers import health, subscriptions, frontend
from .middleware import log_request_middleware

logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(_: FastAPI):
    '''Application lifespan management.'''
    # Print all registered routes
    for route in app.routes:
        if hasattr(route, 'path'):
            logger.info(f'Route: {route.path} | Methods: {getattr(route, 'methods', 'N/A')}')  # pyright: ignore[reportAttributeAccessIssue]
    yield

def create_app() -> FastAPI:
    app = FastAPI(
        title='NotiFER',
        description='A web application allowing students of FER Zagreb to subscribe to email notifications about timetable chagnes.',
        version='3.0.0',
        lifespan=lifespan
    )

    app.middleware('http')(log_request_middleware)

    # Include routers
    app.include_router(health.router)
    app.include_router(subscriptions.router)
    app.include_router(frontend.router)

    # Mount static files
    app.mount('/static', StaticFiles(directory='static'), name='static')

    return app

app = create_app()
