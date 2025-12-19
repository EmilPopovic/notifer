import time
import logging
from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from api.dependencies import verify_notifer_token
from worker.dependencies import get_worker_service
from shared.email_client import get_email_queue_size
from shared.crud import (
    db_healthcheck,
    get_total_subscription_count_no_session,
    get_active_subscription_count_no_session,
    get_total_changes_detected_no_session,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/health', tags=['health'])

@router.get('/')
async def health():
    return {
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }

@router.get('/ready')
async def readiness_check():
    '''Kubernetes-style readiness check.'''
    return {'status': 'ready'}

@router.get('/detailed', dependencies=[Depends(verify_notifer_token)])
async def detailed_health_check():
    '''Detailed health check with dependency verification.'''
    start_time = time.time()
    health_status = {
        'api': 'healthy',
        'database': 'unknown',
        'worker': 'unknown',
    }

    # Check database
    health_status['database'] = 'healthy' if db_healthcheck() else 'unhealthy'
    
    # Check worker
    worker_service = get_worker_service()
    health_status['worker'] = 'healthy' if worker_service and worker_service._running else 'unhealthy'

    # Overall status
    overall_healthy = all(
        status == 'healthy' or status.startswith('healthy')
        for status in health_status.values()
    )

    response_time = time.time() - start_time

    return {
        'status': 'healthy' if overall_healthy else 'unhealthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'services': health_status,
        'response_time_seconds': round(response_time, 3),
        'version': '3.1.0'
    }

@router.get('/stats', dependencies=[Depends(verify_notifer_token)])
async def stats():
    worker_service = get_worker_service()
    
    # Convert worker_last_cycle to human-readable format
    worker_last_cycle_readable = None
    if worker_service.worker_last_cycle:
        worker_last_cycle_readable = datetime.fromtimestamp(
            worker_service.worker_last_cycle, 
            timezone.utc
        ).isoformat()
    
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'total_subscriptions': get_total_subscription_count_no_session(),
        'active_subscriptions': get_active_subscription_count_no_session(),
        'total_changes_detected': get_total_changes_detected_no_session(),
        'email_queue_size': get_email_queue_size(),
        'worker_cycles_total': worker_service.worker_cycles_total,
        'worker_cycle_duration': worker_service.worker_cycle_duration,
        'worker_last_cycle': worker_last_cycle_readable,
        'subscriptions_processed': worker_service.subscriptions_processed,
        'calendar_fetches': worker_service.calendar_fetches,
        'calendar_fetch_duration': worker_service.calendar_fetch_duration,
        'emails_queued': worker_service.emails_queued,
    }
