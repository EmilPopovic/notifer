import os
from cryptography.fernet import Fernet
from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

_fernet: Fernet | None = None


def get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            raise RuntimeError('ENCRYPTION_KEY environment variable must be set')
        _fernet = Fernet(key.encode())
    return _fernet


class EncryptedString(TypeDecorator):
    """Transparently encrypts/decrypts string column values using Fernet (AES-128-CBC + HMAC-SHA256)."""
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return get_fernet().encrypt(value.encode('utf-8')).decode('ascii')

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return get_fernet().decrypt(value.encode('ascii')).decode('utf-8')
