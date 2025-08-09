import os
import logging
import configparser
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from shared.models import Base

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
                'user': db_section.get('user', 'postgres'),
                'host': db_section.get('host', 'postgres'),
                'database': db_section.get('database', 'postgres'),
                'port': db_section.get('port', '5432'),
                'sslmode': db_section.get('sslmode', 'disable')
            }
        else:
            logger.warning("No [database] section found in config file")
            db_config = {}
    else:
        logger.warning(f"Config file not found at {config_path}, using environment variables only")
        db_config = {}
    
    # Get database settings from config file with fallbacks to environment variables
    postgres_user = db_config.get('user') or os.getenv('POSTGRES_USER', 'postgres')
    postgres_host = db_config.get('host') or os.getenv('POSTGRES_HOST', 'postgres')
    postgres_db = db_config.get('database') or os.getenv('POSTGRES_DB', 'postgres')
    postgres_port_str = db_config.get('port') or os.getenv('POSTGRES_PORT', '5432')
    postgres_sslmode = db_config.get('sslmode') or os.getenv('POSTGRES_SSLMODE', 'disable')
    
    # Convert port to integer
    try:
        postgres_port = int(postgres_port_str)
    except (ValueError, TypeError):
        postgres_port = 5432
        logger.warning(f"Invalid port '{postgres_port_str}', using default 5432")
    
    # Get password from environment variable (for security)
    postgres_password = os.getenv('POSTGRES_PASSWORD', '')
    
    if not postgres_password:
        logger.warning("POSTGRES_PASSWORD not set in environment variables")
    
    return {
        'user': postgres_user,
        'password': postgres_password,
        'host': postgres_host,
        'database': postgres_db,
        'port': postgres_port,
        'sslmode': postgres_sslmode
    }

# Load database configuration
db_config = load_database_config()

# Build database URI
DATABASE_URI = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}?sslmode={db_config['sslmode']}"

logger.info(f"Database URI configured: postgresql://{db_config['user']}:***@{db_config['host']}:{db_config['port']}/{db_config['database']}?sslmode={db_config['sslmode']}")

engine = create_engine(
    DATABASE_URI,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_recycle=300,
    pool_pre_ping=True
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
