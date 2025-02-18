import secrets
import hmac
from hashlib import sha256

def generate_csrf_token(secret_key: str = None) -> str:
    # Generate random token
    token = secrets.token_urlsafe(32)

    if secret_key:
        signature = hmac.new(
            secret_key.encode(),
            token.encode(),
            sha256
        ).hexdigest()
        return f"{token}:{signature}"
    return token

def validate_csrf_token(token: str, secret_key: str) -> bool:
    try:
        token_part, signature_part = token.split(":")
        expected_signature = hmac.new(
            secret_key.encode(),
            token_part.encode(),
            sha256
        ).hexdigest()
        return hmac.compare_digest(signature_part, expected_signature)
    except Exception as _:
        return False
