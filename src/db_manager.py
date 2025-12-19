import sys
import logging
from sqlalchemy import MetaData
from .shared.database import engine, Base

logger = logging.getLogger(__name__)

def drop_all_tables(force: bool = False):
    from .shared import models  # noqa: F401

    if not force:
        logger.warning('WARNING: This will DELETE ALL DATA in the database!')
        confirmation = input('Type "yes" to confirm: ')
        if confirmation.lower() != 'yes':
            logger.info('Database reset cancelled')
            return
    
    try:
        logger.warning('Dropping all database tables...')
        
        meta = MetaData()
        meta.reflect(bind=engine)
        meta.drop_all(bind=engine)
        
        Base.metadata.drop_all(bind=engine)
        
        logger.info('All tables dropped successfully!')
    except Exception as e:
        logger.error(f'Failed to drop tables: {e}')
        raise

def create_all_tables():
    from .shared import models  # noqa: F401
    
    try:
        logger.info('Creating all database tables...')
        logger.info(f'Registered tables: {list(Base.metadata.tables.keys())}')
        
        Base.metadata.create_all(bind=engine)
        logger.info('All tables created successfully!')

        logger.info('Created tables:')
        for table_name in Base.metadata.tables.keys():
            logger.info(f'  - {table_name}')

    except Exception as e:
        logger.error(f'Failed to create tables: {e}')
        raise

def reset_database(force: bool = False):
    if not force:
        logger.warning('WARNING: This will DELETE ALL DATA in the database!')
        confirmation = input('Type "yes" to confirm: ')
        if confirmation.lower() != 'yes':
            logger.info('Database reset cancelled')
            return
    
    drop_all_tables(force=force)
    create_all_tables()
    logger.info('Database reset complete!')

def check_database():
    from .shared import models  # noqa: F401
    
    try:
        meta = MetaData()
        meta.reflect(bind=engine)
        
        existing_tables = list(meta.tables.keys())
        expected_tables = list(Base.metadata.tables.keys())
        
        if not existing_tables:
            logger.info('Database is NOT initialized - no tables found')
            return False
        
        logger.info('Database is initialized')
        logger.info(f'Found {len(existing_tables)} table(s):')
        for table_name in existing_tables:
            logger.info(f'  - {table_name}')
        
        missing_tables = set(expected_tables) - set(existing_tables)
        if missing_tables:
            logger.warning(f'Missing expected tables: {", ".join(missing_tables)}')
        
        return True
    except Exception as e:
        logger.error(f'Failed to check database: {e}')
        raise

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'create':
            create_all_tables()
        elif command == 'drop':
            force = '--force' in sys.argv
            drop_all_tables(force=force)
        elif command == 'reset':
            force = '--force' in sys.argv
            reset_database(force=force)
        elif command == 'check':
            check_database()
        else:
            print('Usage:')
            print('  python -m src.db_manager create          # Create all tables')
            print('  python -m src.db_manager drop            # Drop all tables (with confirmation)')
            print('  python -m src.db_manager drop  --force   # Drop all tables (no confirmation)')
            print('  python -m src.db_manager reset           # Drop and recreate (with confirmation)')
            print('  python -m src.db_manager reset --force   # Drop and recreate (no confirmation)')
            print('  python -m src.db_manager check           # Check if database is initialized')
            sys.exit(1)
    else:
        create_all_tables()

if __name__ == '__main__':
    main()
