import os
import logging
import configparser
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .models import Base

logger = logging.getLogger(__name__)

def load_database_config():
    """Load database configuration from app.conf and environment variables."""
    
    # Load configuration from app.conf file
    config_path = Path(__file__).parent.parent / "config" / "app.conf"
    config = configparser.ConfigParser()
    
    if config_path.exists():
        config.read(config_path)
        
        # Get the database section correctly
        if config.has_section('database'):
            db_section = config['database']
            # Convert section to dictionary
            db_config = {
                'path': db_section.get('path', 'data/notifer.db')
            }
        else:
            logger.warning("No [database] section found in config file")
            db_config = {}
    else:
        logger.warning(f"Config file not found at {config_path}, using environment variables only")
        db_config = {}
    
    # Get database settings from config file with fallbacks to environment variables
    db_path = db_config.get('path') or os.getenv('DATABASE_PATH', 'data/notifer.db')
    
    # Ensure the directory exists
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    return {'path': str(db_file.resolve())}

# Load database configuration
db_config = load_database_config()

# Build database URI
DATABASE_URI = f'sqlite:///{db_config['path']}'

logger.info(f'Database configured: {DATABASE_URI}')

engine = create_engine(
    DATABASE_URI,
    poolclass=StaticPool,
    connect_args={
        'check_same_thread': False,
        'timeout': 20
    },
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    logger.info('Initializing database')
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
