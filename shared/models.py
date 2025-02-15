from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UserCalendar(Base):
    __tablename__ = 'user_calendars'

    email = Column(String, primary_key=True, unique=True, nullable=False)
    calendar_auth = Column(String, nullable=False)
    activated = Column(Boolean, default=False, nullable=False)
    paused = Column(Boolean, default=False, nullable=False)
    created = Column(DateTime, default=datetime.now, nullable=False)
    last_checked = Column(DateTime, nullable=True)
    previous_calendar = Column(Text, nullable=True)
    previous_calendar_hash = Column(String, nullable=True)