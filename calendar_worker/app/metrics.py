import logging
from prometheus_client import Counter, Histogram, Gauge, Info, start_http_server, generate_latest, REGISTRY

logger = logging.getLogger(__name__)

try:
    # Clear any existing registrations to avoid conflicts
    REGISTRY._collector_to_names.clear()
    REGISTRY._names_to_collectors.clear()
    logger.info("Cleared Prometheus registry")
except Exception as e:
    logger.warning(f"Could not clear registry: {e}")

# Define metrics at module level (created only once)
WORKER_CYCLES_TOTAL = Counter(
    'calendar_worker_cycles_total',
    'Total number of processing cycles completed',
    ['status']
)

WORKER_CYCLE_DURATION = Histogram(
    'calendar_worker_cycle_duration_seconds',
    'Time spent processing each cycle',
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0]
)

SUBSCRIPTIONS_PROCESSED = Counter(
    'calendar_worker_subscriptions_processed_total',
    'Total number of subscriptions processed',
    ['status']
)

CALENDAR_FETCHES_TOTAL = Counter(
    'calendar_worker_calendar_fetches_total',
    'Total number of calendar fetch attempts',
    ['status']
)

CALENDAR_FETCH_DURATION = Histogram(
    'calendar_worker_calendar_fetch_duration_seconds',
    'Time spent fetching calendars',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

EMAILS_QUEUED_TOTAL = Counter(
    'calendar_worker_emails_queued_total',
    'Total number of emails queued for sending'
)

WORKER_INFO = Info(
    'calendar_worker_info',
    'Information about the calendar worker'
)

WORKER_LAST_CYCLE_TIME = Gauge(
    'calendar_worker_last_cycle_timestamp_seconds',
    'Timestamp of the last completed cycle'
)

ACTIVE_SUBSCRIPTIONS_GAUGE = Gauge(
    'calendar_worker_active_subscriptions',
    'Number of active subscriptions found in last cycle'
)

# Initialize worker info once
try:
    WORKER_INFO.info({
        'version': '2.0.1',
        'worker_type': 'calendar_processor'
    })
    logger.info("Initialized worker info metrics")
except Exception as e:
    logger.warning(f"Could not set worker info: {e}")

def start_metrics_server(port: int = 8001):
    """Start HTTP server for metrics exposure"""
    try:
        start_http_server(port)
        logger.info(f'Metrics server started on port {port}')
    except Exception as e:
        logger.error(f'Failed to start metrics server: {e}')
        # Don't raise the exception - let the worker continue without metrics

def get_metrics():
    """Get current metrics in Prometheus format"""
    try:
        return generate_latest()
    except Exception as e:
        logger.error(f'Error generating metrics: {e}')
        return ""
