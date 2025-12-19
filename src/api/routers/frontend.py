from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import FileResponse
import logging
from api.dependencies import require_component_enabled

logger = logging.getLogger(__name__)
router = APIRouter(tags=['frontend'])

@router.get('/', dependencies=[require_component_enabled('frontend_enabled')])
async def serve_frontend():
    logger.info('Serving frontend index.html')
    return FileResponse('static/index.html')

@router.get('/favicon.ico', include_in_schema=False,
            dependencies=[require_component_enabled('frontend_enabled')])
async def favicon():
    logger.info('Serving favicon')
    return FileResponse('static/favicon.ico')
