import time
import redis
import psycopg2
import logging
import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime, timezone

from ..config import get_settings, Settings
from shared.database import SessionLocal
from shared.models import UserCalendar

logger = logging.getLogger(__name__)
router = APIRouter(tags=['health'])

@router.get('/health')
async def health():
    return {
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'service': 'notifer-api'
    }

@router.get('/health/ready')
async def readiness_check():
    '''Kubernetes-style readiness check.'''
    return {'status': 'ready'}

@router.get('/health/detailed')
async def detailed_health_check(settings: Settings = Depends(get_settings)):
    '''Detailed health check with dependency verification.'''
    start_time = time.time()
    health_status = {
        'api': 'healthy',
        'database': 'unknown',
        'redis': 'unknown',
        'email_queue': 'unknown',
        's3': 'unknown'
    }

    # Check database
    try:
        conn_string = f'postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}'
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        cursor.close()
        conn.close()
        health_status['database'] = 'healthy'
    except Exception as e:
        health_status['database'] = f'unhealthy: {str(e)}'

    # Check Redis
    try:
        r = redis.Redis.from_url(settings.redis_url)
        r.ping()
        health_status['redis'] = 'healthy'

        # Check email queue
        queue_size = r.llen('rq:queue:email')
        health_status['email_queue'] = f'healthy (queue size: {queue_size})'
    except Exception as e:
        health_status['redis'] = f'unhealthy: {str(e)}'
        health_status['email_queue'] = 'unhealthy: redis unavailable'

    # Check S3/MinIO
    try:
        response = requests.get(f'{settings.s3_endpoint}/minio/health/live', timeout=5)
        if response.status_code == 200:
            health_status['s3'] = 'healthy'
        else:
            health_status['s3'] = f'unhealthy: status {response.status_code}'
    except Exception as e:
        health_status['s3'] = f'unhealthy: {str(e)}'

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
        'version': '2.0.0'
    }

@router.get('/metrics/custom')
async def custom_metrics(settings: Settings = Depends(get_settings)):
    '''Custom application metrics from Prometheus.'''
    try:
        # Get active subscription count
        session = SessionLocal()
        try:
            active_count = session.query(UserCalendar).filter(
                UserCalendar.activated == True,
                UserCalendar.paused == False
            ).count()
            total_count = session.query(UserCalendar).count()
        finally:
            session.close()

        # Get emai queue size
        r = redis.Redis.from_url(settings.redis_url)
        queue_size = r.llen('rq:queue:email')

        return {
            'active_subscriptions': active_count,
            'total_subscriptions': total_count,
            'email_queue_size': queue_size,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error collecting metrics: {str(e)}')

@router.post('/webhook')
async def alertmanager_webhook(request: Request):
    '''Receive alertmanager webhook notifications.'''
    try:
        payload = await request.json()
        logger.info(f'Received alert: {payload.get('status', 'unknown')} - {len(payload.get('alerts', []))} alerts')
        
        for alert in payload.get('alerts', []):
            alert_name = alert.get('labels', {}).get('alertname', 'Unknown')
            status = alert.get('status', 'unknown')
            logger.warning(f'Alert: {alert_name} is {status}')
            
        return {'status': 'received'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
