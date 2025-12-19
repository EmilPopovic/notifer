import pytz
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from shared.models import UserCalendar
from shared.database import SessionLocal

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
        previous_calendar_path=None,
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
