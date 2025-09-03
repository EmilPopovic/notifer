from sqlalchemy import String, Boolean, DateTime, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class UserCalendar(Base):
    __tablename__ = 'user_calendars'
    __table_args__ = (
        {'sqlite_autoincrement': True}
    )

    username: Mapped[str] = mapped_column(String, nullable=False, primary_key=True)
    domain: Mapped[str] = mapped_column(String, default='fer.hr', nullable=False, primary_key=True)
    calendar_auth: Mapped[str] = mapped_column(String, nullable=False)
    activated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    paused: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now, nullable=False)
    last_checked: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    last_change_detected: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    change_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    previous_calendar_url: Mapped[str | None] = mapped_column(String, nullable=True)
    previous_calendar_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    language: Mapped[str] = mapped_column(String, default='hr', nullable=False)

    @property
    def email(self) -> str:
        return f'{self.username}@{self.domain}'

class ResendUsage(Base):
    __tablename__ = 'resend_usage'

    date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
