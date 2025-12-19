import os
import jwt
from datetime import datetime, timedelta, timezone

JWT_KEY = os.getenv('JWT_KEY', 'super_secret_key')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
TOKEN_EXPIRATION_MINUTES = int(os.getenv('TOKEN_EXPIRATION_MINUTES', 60))

class TokenValidationError(Exception):
    """Raised when a token fails validation."""
    pass

class TokenExpiredError(TokenValidationError):
    """Raised when a token has expired."""
    pass

def create_token(email: str, action: str) -> str:
    """
    Generates a JWT token for a given email and action ('activate' or 'delete').
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
    payload = {"sub": email, "action": action, "exp": expire}
    return jwt.encode(payload, JWT_KEY, algorithm=ALGORITHM)

def decode_token(token: str, expected_action: str) -> str:
    """
    Decodes a JWT token and verifies the action type.
    Raises TokenValidationError or TokenExpiredError on failure.
    """
    try:
        payload = jwt.decode(token, JWT_KEY, algorithms=[ALGORITHM])
        if payload.get("action") != expected_action:
            raise TokenValidationError("Invalid token action")
        email = payload.get("sub")
        if not email:
            raise TokenValidationError("Invalid token payload")
        return email
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token has expired")
    except Exception:
        raise TokenValidationError("Invalid token")
