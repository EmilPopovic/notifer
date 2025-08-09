#!/usr/bin/env python3
'''Entry point for the worker.'''

if __name__ == '__main__':
    from app.config import get_settings
    settings = get_settings()
    if not settings.worker_enabled:
        exit(0)
    from app.main import start_worker
    start_worker()
