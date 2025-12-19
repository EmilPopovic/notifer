import datetime
from sqlalchemy import String, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserCalendar(Base):
    __tablename__ = 'user_calendars'

    username: Mapped[str] = mapped_column(
        String,
        nullable=False,
        primary_key=True
    )

    domain: Mapped[str] = mapped_column(
        String,
        default='fer.hr',
        nullable=False,
        primary_key=True
    )

    calendar_auth: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    activated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    paused: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.now,
     
        nullable=False
    )

    last_checked: Mapped[datetime.datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    last_change_detected: Mapped[datetime.datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    change_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    previous_calendar_path: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )
    
    previous_calendar_hash: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    language: Mapped[str] = mapped_column(
        String,
        default='hr',
        nullable=False
    )

    @property
    def email(self) -> str:
        return f'{self.username}@{self.domain}'
