from pydantic import BaseModel
from typing import Any
from api.exceptions import ErrorCode

class ErrorResponse(BaseModel):
    error_code: ErrorCode
    details: dict[str, Any] | None

class SubscriptionResponse(BaseModel):
    status: str
    email: str

class HealthResponse(BaseModel):
    status: str
    error_code: ErrorCode | None = None
    detail: dict[str, Any] | None = None

class EmailSentResponse(BaseModel):
    message: str
