from fastapi import APIRouter, Body, Depends, HTTPException, status
import logging
from api.dependencies import (
    SubscriptionService,
    get_subscription_service,
    verify_notifer_token,
    require_component_enabled,
)
from api.schemas import SubscriptionResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/admin', tags=['admin'])

@router.post('/subscribe/url',
             dependencies=[Depends(verify_notifer_token), require_component_enabled('admin_api_enabled')],
             response_model=SubscriptionResponse)
async def admin_subscribe_by_url(
    q: str = Body(..., embed=True),
    language: str = Body('hr', embed=True),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    '''Admin API: Add subscription by calendar URL (activated by default).'''
    logger.info(f'API subscribe request with {q[:30]}... in language {language}')
    try:
        email = subscription_service.create_subscription_from_url(q, language, activated=True)
        return SubscriptionResponse(status='ok', email=email)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post('/subscribe/username',
             dependencies=[Depends(verify_notifer_token), require_component_enabled('admin_api_enabled')],
             response_model=SubscriptionResponse)
async def admin_subscribe_by_username(
    username: str = Body(..., embed=True),
    auth: str = Body(..., embed=True),
    language: str = Body('hr', embed=True),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    '''Admin API: Add subscription by username and calendar auth (activated by default).'''
    logger.info(f'API subscribe request with user {username} and auth {auth[:5]}... in language {language}')
    try:
        email = subscription_service.create_subscription_from_uname_and_auth(username, auth, language, activated=True)
        return SubscriptionResponse(status='ok', email=email)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post('/pause',
             dependencies=[Depends(verify_notifer_token), require_component_enabled('admin_api_enabled')])
async def admin_pause_by_username(
    username: str = Body(..., embed=True),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    '''Pause a subscription by username.'''
    try:
        subscription_service.pause_subscription_by_username(username)
        return {"status": "ok", "action": "paused"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post('/resume',
             dependencies=[Depends(verify_notifer_token), require_component_enabled('admin_api_enabled')])
async def admin_resume_by_username(
    username: str = Body(..., embed=True),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    '''Resume a subscription by username.'''
    try:
        subscription_service.resume_subscription_by_username(username)
        return {"status": "ok", "action": "resumed"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post('/delete',
             dependencies=[Depends(verify_notifer_token), require_component_enabled('admin_api_enabled')])
async def admin_delete_by_username(
    username: str = Body(..., embed=True),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    '''Delete a subscription by username.'''
    try:
        subscription_service.delete_subscription_by_username(username)
        return {"status": "ok", "action": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get('/info',
            dependencies=[Depends(verify_notifer_token), require_component_enabled('admin_api_enabled')])
async def admin_get_info_by_username(
    username: str,
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    '''Get subscription info by username.'''
    try:
        info = subscription_service.get_subscription_info_by_username(username)
        return info
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.get('/info/all',
            dependencies=[Depends(verify_notifer_token), require_component_enabled('allow_query_all_enabled'), require_component_enabled('admin_api_enabled')])
async def admin_get_all_info(subscription_service: SubscriptionService = Depends(get_subscription_service)):
    '''Get info about all subscribers.'''
    try:
        info = subscription_service.get_all()
        return info
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
