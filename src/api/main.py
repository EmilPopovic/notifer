import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from config import get_settings
from api.routers import health, subscriptions, frontend, admin
from api.middleware import log_request_middleware

logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(_: FastAPI):
    # Print all registered routes
    for route in app.routes:
        if hasattr(route, 'path'):
            logger.info(f'Route: {route.path} | Methods: {getattr(route, 'methods', 'N/A')}')  # pyright: ignore[reportAttributeAccessIssue]
    yield

def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.middleware('http')(log_request_middleware)

    app.include_router(health.router)
    app.include_router(subscriptions.router)
    app.include_router(frontend.router)
    app.include_router(admin.router)

    app.mount('/static', StaticFiles(directory='static'), name='static')

    return app

app = create_app()
