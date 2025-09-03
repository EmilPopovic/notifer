import pytz
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from shared.models import UserCalendar, ResendUsage
from .database import get_db, SessionLocal

def db_healthcheck() -> bool:
    """
    Simple health check for the database connection.
    Returns True if database is reachable and a query can be executed, False otherwise.
    """
    try:
        session = SessionLocal()
        session.execute(text('SELECT 1'))
        session.close()
        return True
    except Exception as _:
        return False

# region calendars

def create_subscription(
        db: Session,
        username: str,
        domain: str,
        calendar_auth: str,
        language: str = 'hr',
        activated: bool = False
) -> UserCalendar:
    """Create a new user subscription entry."""
    new_sub = UserCalendar(
        username=username,
        domain=domain,
        calendar_auth=calendar_auth,
        activated=activated,
        paused=False,
        created=datetime.now(tz=pytz.timezone('Europe/Paris')),
        last_checked=None,
        previous_calendar_url=None,
        previous_calendar_hash=None,
        language=language
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return new_sub

def get_subscription_by_username(db: Session, username: str, domain: str = 'fer.hr') -> UserCalendar | None:
    """Retreive a subscription for the given email."""
    return db.query(UserCalendar).filter(UserCalendar.username == username, UserCalendar.domain == domain).first()

def get_subscription(db: Session, email: str) -> UserCalendar | None:
    """Retrieve a subscription for a given email (username@domain)"""
    if '@' not in email:
        return None
    
    username, domain = email.split('@', 1)
    return get_subscription_by_username(db, username, domain)

def get_total_changes_detected(db: Session) -> int:
    count = db.query(func.sum(UserCalendar.change_count)).scalar()
    return count or 0

def get_total_changes_detected_no_session() -> int:
    session = SessionLocal()
    try:
        return get_total_changes_detected(session)
    except Exception as _:
        return 0
    finally:
        session.close()

def get_all_subscriptions(db: Session) -> list[UserCalendar]:
    """Retreive all subscriptions."""
    return db.query(UserCalendar).all()

def get_all_subscriptions_no_session(expunge_all: bool = True) -> list[UserCalendar]:
    session = SessionLocal()
    try:
        subs = get_all_subscriptions(session)
        if expunge_all:
            session.expunge_all()
        return subs
    except Exception as _:
        return []
    finally:
        session.close()

def get_active_subscriptions(db: Session) -> list[UserCalendar]:
    return db.query(UserCalendar).filter(UserCalendar.activated.is_(True), UserCalendar.paused.is_(False)).all()

def get_active_subscriptions_no_session(expunge_all: bool = True) -> list[UserCalendar]:
    session = SessionLocal()
    try:
        subs = get_active_subscriptions(session)
        if expunge_all:
            session.expunge_all()
        return subs
    except Exception as _:
        return []
    finally:
        session.close()

def get_total_subscription_count(db: Session) -> int:
    subs = get_all_subscriptions(db)
    return len(subs)

def get_total_subscription_count_no_session() -> int:
    session = SessionLocal()
    try:
        count = get_total_subscription_count(session)
        return count
    except Exception as _:
        return 0
    finally:
        session.close()

def get_active_subscription_count(db: Session) -> int:
    active_subs = get_active_subscriptions(db)
    return len(active_subs)

def get_active_subscription_count_no_session() -> int:
    session = SessionLocal()
    try:
        count = get_total_subscription_count(session)
        return count
    except Exception as _:
        return 0
    finally:
        session.close()

def get_user_language(db: Session, email: str) -> str:
    """Get preferred language, defaulting to Croatian."""
    subscription = get_subscription(db, email)
    if subscription and subscription.language:
        return subscription.language
    return 'hr'

def update_user_language(db: Session, email: str, language: str) -> bool:
    """Update user's language preference."""
    subscription = get_subscription(db, email)
    if subscription:
        subscription.language = language
        db.commit()
        return True
    return False

def update_activation(db: Session, email: str, activated: bool) -> UserCalendar | None:
    """Update the 'activated' status for a given user subscription."""
    sub = get_subscription(db, email)
    if not sub:
        return None

    sub.activated = activated
    db.commit()
    db.refresh(sub)
    return sub

def update_paused(db: Session, email: str, paused: bool) -> UserCalendar | None:
    """Update the 'paused' status for a given user subscription."""
    sub = get_subscription(db, email)
    if not sub:
        return None

    sub.paused = paused
    db.commit()
    db.refresh(sub)
    return sub

def update_calendar_url(db: Session, email: str, new_calendar_url: str, new_calendar_hash: str) -> UserCalendar | None:
    """Update the stored calendar content, hash, and last check time for a user."""
    sub = get_subscription(db, email)
    if not sub:
        return None

    sub.previous_calendar = new_calendar_url
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
    sub = get_subscription(db, email)
    if not sub:
        return False

    db.delete(sub)
    db.commit()
    return True

# endregion
# region resend usage

def get_resend_usage_for_date(db: Session, usage_date: date) -> int:
    record = db.query(ResendUsage).filter(ResendUsage.date == usage_date).first()
    return record.count if record else 0

def get_monthly_resend_usage(db: Session, start_date: date) -> int:
    total = db.query(func.sum(ResendUsage.count)).filter(ResendUsage.date >= start_date).scalar()
    return total or 0

def increment_resend_usage(db: Session, usage_date: date):
    record = db.query(ResendUsage).filter(ResendUsage.date == usage_date).first()
    if record:
        record.count += 1
    else:
        record = ResendUsage(date=usage_date, count=1)
        db.add(record)
    db.commit()

def can_send_with_resend(daily_limit: int = 95, monthly_limit: int = 2950) -> bool:
    """
    Check if we can send email with Resend based on usage limits.
    Returns True if within limits, False otherwise
    """
    db = next(get_db())
    try:
        today = date.today()
        start_of_month = today.replace(day=1)

        daily_count = get_resend_usage_for_date(db, today)
        monthly_count = get_monthly_resend_usage(db, start_of_month)

        return daily_count < daily_limit and monthly_count < monthly_limit
    except Exception as _:
        return False
    finally:
        db.close()

def update_resend_usage():
    """
    Update Resend usage count for today.
    This should be called after successfully sending an email via Resend
    """
    db = next(get_db())
    try:
        today = date.today()
        increment_resend_usage(db, today)
    except Exception as _:
        db.rollback()
    finally:
        db.close()

# endregion
