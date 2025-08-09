from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import FileResponse
import logging

from ..config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=['frontend'])

settings = get_settings()

def require_component_enabled(component: str):
    def dependency():
        if not getattr(settings, component):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'{component.replace('_enabled', '').replace('_', ' ').capitalize()}'
            )
    return Depends(dependency)

@router.get('/', dependencies=[require_component_enabled('frontend_enabled')])
async def serve_frontend():
    logger.info('Serving frontend index.html')
    return FileResponse('static/index.html')

@router.get('/favicon.ico', include_in_schema=False,
            dependencies=[require_component_enabled('frontend_enabled')])
async def favicon():
    logger.info('Serving favicon')
    return FileResponse('static/favicon.ico')
