import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared.models import Base
from shared.secrets import get_secret

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = get_secret('POSTGRES_PASSWORD_FILE')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')

DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    if os.getenv('DEV', 'false').lower() in ['true', '1', 'yes']:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
