from fastapi import HTTPException
from enum import Enum

class ErrorCode(str, Enum):
    SUBSCRIPTION_NOT_FOUND = 'SUBSCRIPTION_NOT_FOUND'
    SUBSCRIPTION_ALREADY_ACTIVE = 'SUBSCRIPTION_ALREADY_ACTIVE'
    INVALID_CALENDAR_URL = 'INVALID_CALENDAR_URL'
    INVALID_ICAL_DOCUMENT = 'INVALID_ICAL_DOCUMENT'
    NOTIFICATIONS_ALREADY_PAUSED = 'NOTIFICATIONS_ALREADY_PAUSED'
    NOTIFICATIONS_ALREADY_ACTIVE = 'NOTIFICATIONS_ALREADY_ACTIVE'
    RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED'
    INVALID_TOKEN = 'INVALID_TOKEN'

class LocalizedHTTPException(HTTPException):
    def __init__(self, status_code: int, error_code: ErrorCode, details: dict | None = None):
        self.error_code = error_code
        self.details = details if details is not None else {}
        super().__init__(
            status_code=status_code,
            detail={
                'error_code': error_code,
                'details': details
            }
        )

class SubscriptionNotFoundError(LocalizedHTTPException):
    def __init__(self):
        super().__init__(404, ErrorCode.SUBSCRIPTION_NOT_FOUND)

class SubscriptionAlreadyActiveError(LocalizedHTTPException):
    def __init__(self):
        super().__init__(400, ErrorCode.SUBSCRIPTION_ALREADY_ACTIVE)

class NotificationsAlreadyPausedError(LocalizedHTTPException):
    def __init__(self):
        super().__init__(400, ErrorCode.NOTIFICATIONS_ALREADY_PAUSED)

class NotificationsAlreadyActiveError(LocalizedHTTPException):
    def __init__(self):
        super().__init__(400, ErrorCode.NOTIFICATIONS_ALREADY_ACTIVE)

class InvalidTokenError(LocalizedHTTPException):
    def __init__(self):
        super().__init__(403, ErrorCode.INVALID_TOKEN, {'message': 'This link is invalid or expired'})

class InvalidCalendarUrlError(LocalizedHTTPException):
    def __init__(self, message: str | None = None):
        super().__init__(400, ErrorCode.INVALID_CALENDAR_URL, {'message': message})

class RateLimitExceededError(LocalizedHTTPException):
    def __init__(self, retry_after_minutes: int):
        super().__init__(
            429,
            ErrorCode.RATE_LIMIT_EXCEEDED,
            {'retry_after_minutes': retry_after_minutes}
        )
