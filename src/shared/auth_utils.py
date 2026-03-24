import hashlib
import hmac
import os
import jwt
from datetime import datetime, timedelta, timezone

COOKIE_NAME = 'ds'
_SESSION_HOURS = 8


def hash_password(password: str) -> str:
    """Hash a password for storage in the env file. Returns 'salt_hex:hash_hex'."""
    salt = os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        bytes.fromhex(salt),
        260_000,
    ).hex()
    return f'{salt}:{digest}'


def verify_password(password: str, stored: str) -> bool:
    """Verify a password against its stored 'salt_hex:hash_hex'."""
    try:
        salt_hex, hash_hex = stored.split(':', 1)
        expected = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            bytes.fromhex(salt_hex),
            260_000,
        ).hex()
        return hmac.compare_digest(expected, hash_hex)
    except Exception:
        return False


def create_session_token(jwt_key: str) -> str:
    payload = {
        'sub': 'dashboard',
        'exp': datetime.now(timezone.utc) + timedelta(hours=_SESSION_HOURS),
    }
    return jwt.encode(payload, jwt_key, algorithm='HS256')


def verify_session_token(token: str, jwt_key: str) -> bool:
    try:
        jwt.decode(token, jwt_key, algorithms=['HS256'])
        return True
    except Exception:
        return False
