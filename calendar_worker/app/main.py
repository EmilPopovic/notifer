import logging
import signal
import sys
from threading import Thread
from flask import Flask
import time

from shared.database import init_db
from calendar_worker.app.dependencies import get_worker_service

from calendar_worker.app.metrics import start_metrics_server

# Configure logging
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

app = Flask(__name__)

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': time.time()}, 200

def signal_handler(signum, _):
    logger.info(f'Received signal {signum}, shutting down...')
    sys.exit(0)

def start_health_server(port: int = 8002):
    app.run(host='0.0.0.0', port=port)

def start_worker():
    '''Main application entry point.'''
    logger.info('Calendar worker starting up')

    metrics_thread = Thread(target=start_metrics_server, args=(8001,), daemon=True)
    metrics_thread.start()

    health_thread = Thread(target=start_health_server, args=(8002,), daemon=True)
    health_thread.start()

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        logger.info('Initializing database')
        init_db()

        # Get worker service and run
        worker_service = get_worker_service()
        worker_service.run_continuously()

    except KeyboardInterrupt:
        logger.info('Received keyboard interrupt, shutting down...')
    except Exception as e:
        logger.error(f'Critical error: {e}')
        sys.exit(1)
