import logging
import signal
import sys

from shared.database import init_db
from worker.dependencies import get_worker_service

logger = logging.getLogger(__name__)

def setup_signal_handlers():
    """Set up signal handlers for graceful shutdown"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def signal_handler(signum, _):
    """Handle termination signals"""
    logger.info(f'Received signal {signum}, shutting down...')
    sys.exit(0)

def start_worker():
    """Start the worker process"""
    logger.info('Calendar worker starting up')

    try:
        worker_service = get_worker_service()
        worker_service.run_continuously()
    except KeyboardInterrupt:
        logger.info('Received keyboard interrupt, shutting down...')
    except Exception as e:
        logger.error(f'Critical error: {e}')
        sys.exit(1)

# This is used when running the worker standalone
if __name__ == '__main__':
    from config import get_settings
    settings = get_settings()
    if not settings.worker_enabled:
        exit(0)

    # Configure logging here when running standalone
    LOG_FORMAT = (
        "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | "
        "%(funcName)s() | %(threadName)s | %(message)s"
    )
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
    
    init_db()
    setup_signal_handlers()
    start_worker()
