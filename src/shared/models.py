import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserCalendar(Base):
    __tablename__ = 'user_calendars'
    __table_args__ = (
        # Worker's main query filters on both columns every polling cycle
        Index('ix_user_calendars_activated_paused', 'activated', 'paused'),
    )

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

    # TODO: calendar_auth is stored in plaintext — if the DB is dumped all users'
    # FER calendar credentials are exposed. Should be encrypted at rest.
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


class AuditLog(Base):
    __tablename__ = 'audit_log'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True
    )

    email: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        index=True
    )

    action: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    details: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )
