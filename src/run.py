#!/usr/bin/env python3
import sys
import threading
import logging
import uvicorn
import signal
import time

from api.main import create_app
from worker.dependencies import get_worker_service
from shared.database import init_db

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

threads: list[threading.Thread] = []

def signal_handler(signum, _):
    """Handle termination signals by stopping all threads gracefully"""
    logger.info(f'Received sinal {signum}, shutting down...')

    for thread in threads:
        if hasattr(thread, 'stop'):
            thread.stop() # type: ignore
    sys.exit(0)

def start_api_thread():
    """Start the API server in a thread"""
    app = create_app()
    config = uvicorn.Config(app, host='0.0.0.0', port=8026, log_level='info')
    server = uvicorn.Server(config)
    logger.info('Starting API server thread')
    server.run()

def start_worker_thread():
    """Start the worker in a thread"""
    logger.info('Starting worker thread')
    worker_service = get_worker_service()
    worker_service.run_continuously()

def main():
    """Main application entry point"""
    logger.info('Starting NotiFER unified service')

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize database for both services
    logger.info('Initializing database')
    init_db()

    # Start API thread
    api_thread = threading.Thread(target=start_api_thread, name='ApiThread')
    api_thread.daemon = True
    api_thread.start()
    threads.append(api_thread)

    # Start worker thread
    worker_thread = threading.Thread(target=start_worker_thread, name='WorkerThread')
    worker_thread.daemon = True
    worker_thread.start()
    threads.append(worker_thread)

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('Keyboard interrupt received, shutting down...')
    except Exception as e:
        logger.error(f'Error in main thread: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
