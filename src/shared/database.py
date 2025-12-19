import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from .models import Base

logger = logging.getLogger(__name__)

USER = os.getenv('POSTGRES_USER', 'postgres')
PASSWORD = os.getenv('POSTGRES_PASSWORD', '')
HOST = os.getenv('POSTGRES_HOST', 'postgres')
PORT = os.getenv('POSTGRES_PORT', '5432')
DATABASE = os.getenv('POSTGRES_DB', 'postgres')
SSLMODE = os.getenv('POSTGRES_SSLMODE', 'disable')

DATABASE_URI = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?sslmode={SSLMODE}"

logger.info(f"Database URI configured: postgresql://{USER}:***@{HOST}:{PORT}/{DATABASE}?sslmode={SSLMODE}")

engine = create_engine(
    DATABASE_URI,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_recycle=300,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
