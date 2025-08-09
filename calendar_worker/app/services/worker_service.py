import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from shared.database import SessionLocal
from shared.models import UserCalendar
from .calendar_service import CalendarService

from calendar_worker.app.metrics import (
    WORKER_CYCLES_TOTAL,
    WORKER_CYCLE_DURATION,
    WORKER_LAST_CYCLE_TIME,
    ACTIVE_SUBSCRIPTIONS_GAUGE,
    SUBSCRIPTIONS_PROCESSED,
    CALENDAR_FETCHES_TOTAL,
    CALENDAR_FETCH_DURATION,
    EMAILS_QUEUED_TOTAL
)

logger = logging.getLogger(__name__)
    
def record_cycle_complete(start_time: float, status: str = 'success', subscription_count: int = 0):
    """Record completion of a processing cycle"""
    try:
        duration = time.time() - start_time
        
        WORKER_CYCLES_TOTAL.labels(status=status).inc()
        WORKER_CYCLE_DURATION.observe(duration)
        WORKER_LAST_CYCLE_TIME.set(time.time())
        ACTIVE_SUBSCRIPTIONS_GAUGE.set(subscription_count)
        
        logger.info(f'Cycle completed: status={status}, duration={duration:.2f}s, subscriptions={subscription_count}')
    except Exception as e:
        logger.error(f'Error recording cycle metrics: {e}')

def record_subscription_processed(status: str):
    """Record processing of a subscription"""
    try:
        SUBSCRIPTIONS_PROCESSED.labels(status=status).inc()
    except Exception as e:
        logger.error(f'Error recording subscription metric: {e}')

def record_calendar_fetch(status: str, duration: float):
    """Record calendar fetch attempt"""
    try:
        CALENDAR_FETCHES_TOTAL.labels(status=status).inc()
        CALENDAR_FETCH_DURATION.observe(duration)
    except Exception as e:
        logger.error(f'Error recording calendar fetch metrics: {e}')

def record_email_queued():
    """Record email being queued"""
    try:
        EMAILS_QUEUED_TOTAL.inc()
    except Exception as e:
        logger.error(f'Error recording email queued metric: {e}')

class WorkerService:
    '''Service for managing the main worker loop.'''

    def __init__(self, calendar_service: CalendarService, worker_interval: int, max_workers: int = 10):
        self.calendar_service = calendar_service
        self.worker_interval = worker_interval
        self.max_workers = max_workers
        self._running = False

    def get_active_subscriptions(self) -> List[UserCalendar]:
        '''Retrieve all subscriptions from database.'''
        session = SessionLocal()
        try:
            subscriptions = session.query(UserCalendar).all()
            # Expunge all objeccts so they can be used outside the session
            session.expunge_all()
            return subscriptions
        except Exception as e:
            logger.exception(f'Error retrieving subscriptions: {e}')
            return []
        finally:
            session.close()

    def process_subscription_with_metrics(self, subscription: UserCalendar) -> dict:
        '''Process single subscription with metrics tracking.'''
        start_time = time.time()

        try:
            result = self.calendar_service.process_subscription(subscription)
            duration = time.time() - start_time

            if result['error'] is None:
                record_subscription_processed('processed')
                record_calendar_fetch('success', duration)

                if result['email_queued']:
                    record_email_queued()
            else:
                record_subscription_processed('error')
                record_calendar_fetch('error', duration)

            return result
        
        except Exception as e:
            duration = time.time() - start_time
            record_subscription_processed('error')
            record_calendar_fetch('error', duration)
            logger.exception(f'Error processing subscription {subscription.email}: {e}')
            return {'error': 'UNDOCUMENTED_ERROR'}

    def process_subscription_batch(self, subscriptions: List[UserCalendar]) -> None:
        '''Process a batch of subscriptions using ThreadPoolExecutor.'''
        if not subscriptions:
            logger.info('No subscriptions to process')
            return
        
        logger.info(f'Processing {len(subscriptions)} subscriptions with {self.max_workers} workers')

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = {
                executor.submit(self.process_subscription_with_metrics, sub): sub
                for sub in subscriptions
            }

            # Processs completed tasks
            successful = 0
            failed = 0
            for future in as_completed(futures):
                subscription = futures[future]
                try:
                    success = future.result()
                    if success['error'] is None:
                        successful += 1
                    else:
                        failed += 1

                except Exception as e:
                    logger.exception(f'Unhandled error processing subscription for {subscription.email}: {e}')
                    failed += 1

            logger.info(f'Batch processing complete: {successful} successful, {failed} failed')

    def run_single_cycle(self) -> bool:
        '''Run a single processing cycle'''
        logger.info('Starting processing cycle')
        cycle_start = time.time()

        try:
            # Get all subscriptions
            subscriptions = self.get_active_subscriptions()
            if not subscriptions:
                logger.info('No subscriptions found')
                record_cycle_complete(cycle_start, 'success', 0)
                return True
            
            logger.info(f'Found {len(subscriptions)} subscriptions')

            # Process subscriptions in parallel
            self.process_subscription_batch(subscriptions)

            record_cycle_complete(cycle_start, 'success', len(subscriptions))
            logger.info('Processing cycle complete')
            return True
        
        except Exception as e:
            logger.exception(f'Error in processing cycle: {e}')
            record_cycle_complete(cycle_start, 'error', 0)
            return False
    
    def run_continuously(self) -> None:
        '''Run the worker in continuous mode.'''
        logger.info(f'Worker started with a {self.worker_interval}-second interval')

        while True:
            try:
                cycle_start = time.time()

                # Run processing cycle
                self.run_single_cycle()

                # Calculate sleep time (ensure minimum interval)
                cycle_duration = time.time() - cycle_start
                sleep_time = max(0, self.worker_interval - cycle_duration)

                if sleep_time > 0:
                    logger.info(f'Cycle took {cycle_duration:.2f}s. Sleeping for {sleep_time:.2f}s')
                    time.sleep(sleep_time)
                else:
                    logger.warning(f'Cycle took {cycle_duration:.2f}s, longer than interval {self.worker_interval}s')

            except KeyboardInterrupt:
                logger.info('Worker shutdown requested (KeyboardInterrupt). Exiting.')
                break
            except Exception as e:
                logger.exception(f'Unexpected error in worker loop: {e}')
                cycle_start_time = time.time()
                record_cycle_complete(cycle_start_time, 'critical_error', 0)
                logger.info(f'Sleeping for {self.worker_interval} seconds before retry')
                time.sleep(self.worker_interval)
