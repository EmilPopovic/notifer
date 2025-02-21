import pytz
from datetime import datetime, date
from sqlalchemy import func
from sqlalchemy.orm import Session
from shared.models import UserCalendar, ResendUsage


def create_subscription(db: Session, email: str, calendar_auth: str) -> UserCalendar:
    """
    Create a new user subscription entry.
    """
    new_sub = UserCalendar(
        email=email,
        calendar_auth=calendar_auth,
        activated=False,
        paused=False,
        created=datetime.now(tz=pytz.timezone('Europe/Paris')),
        last_checked=None,
        previous_calendar=None,
        previous_calendar_hash=None
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return new_sub


def get_subscription(db: Session, email: str) -> UserCalendar | None:
    """
    Retreive a subscription for the given email.
    """
    return db.query(UserCalendar).filter(UserCalendar.email == email).first()


def update_activation(db: Session, email: str, activated: bool) -> UserCalendar | None:
    """
    Update the 'activated' status for a given user subscription.
    """
    sub = db.query(UserCalendar).filter_by(email=email).first()
    if not sub:
        return None

    sub.activated = activated
    db.commit()
    db.refresh(sub)
    return sub


def update_paused(db: Session, email: str, paused: bool) -> UserCalendar | None:
    """
    Update the 'paused' status for a given user subscription.
    """
    sub = db.query(UserCalendar).filter_by(email=email).first()
    if not sub:
        return None

    sub.paused = paused
    db.commit()
    db.refresh(sub)
    return sub


def update_calendar(db: Session, email: str, new_calendar_content: str, new_calendar_hash: str) -> UserCalendar | None:
    """
    Update the stored calendar content, hash, and last check time for a user.
    """
    sub = db.query(UserCalendar).filter_by(email=email).first()
    if not sub:
        return None

    sub.previous_calendar = new_calendar_content
    sub.previous_calendar_hash = new_calendar_hash
    sub.last_checked = datetime.utcnow()

    db.commit()
    db.refresh(sub)
    return sub


def delete_user(db: Session, email: str) -> bool:
    """
    Delete a user subscription entry.
    Returns True if successful, False if the user does not exist.
    """
    sub = db.query(UserCalendar).filter_by(email=email).first()
    if not sub:
        return False

    db.delete(sub)
    db.commit()
    return True


def get_resend_usage_for_date(db: Session, usage_date: date) -> int:
    record = db.query(ResendUsage).filter(ResendUsage.date == usage_date).first()
    return record.count if record else 0

def get_monthly_resend_usage(db: Session, start_date: date) -> int:
    total = db.query(func.sum(ResendUsage.count)).filter(ResendUsage.date >= start_date).scalar()
    return total if total else 0

def increment_resend_usage(db: Session, usage_date: date):
    record = db.query(ResendUsage).filter(ResendUsage.date == usage_date).first()
    if record:
        record.count += 1
    else:
        record = ResendUsage(date=usage_date, count=1)
        db.add(record)
    db.commit()
