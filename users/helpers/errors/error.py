# core/errors.py
from typing import Any, Optional


class AppError(Exception):
    """Base error for app-level exceptions. Contains HTTP status and safe message."""
    status_code: int = 500
    code: str = "error"
    safe_message: str = "Internal server error"
    extra: Optional[Any] = None

    def __init__(self, safe_message: Optional[str] = None, code: Optional[str] = None, status_code: Optional[int] = None, extra: Any = None):
        if safe_message:
            self.safe_message = safe_message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        self.extra = extra
        super().__init__(self.safe_message)


class BadRequestError(AppError):
    status_code = 400
    code = "bad_request"


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class UnauthorizedError(AppError):
    status_code = 401
    code = "unauthorized"


class ForbiddenError(AppError):
    status_code = 403
    code = "forbidden"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class ValidationError(AppError):
    status_code = 422
    code = "validation_error"


class DatabaseError(AppError):
    status_code = 500
    code = "database_error"
    safe_message = "Database error"
