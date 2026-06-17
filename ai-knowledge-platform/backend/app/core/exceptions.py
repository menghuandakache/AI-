"""Unified exception definitions for the application."""


class BusinessException(Exception):
    """Base business exception with error code and message."""

    def __init__(self, message: str, code: str = "BUSINESS_ERROR", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(BusinessException):
    """Resource not found exception."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, code="NOT_FOUND", status_code=404)


class PermissionDeniedException(BusinessException):
    """Permission denied exception."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, code="PERMISSION_DENIED", status_code=403)


class ValidationException(BusinessException):
    """Parameter validation exception."""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message, code="VALIDATION_ERROR", status_code=422)


class FileParseException(BusinessException):
    """File parsing exception."""

    def __init__(self, message: str = "File parse error"):
        super().__init__(message, code="FILE_PARSE_ERROR", status_code=400)


class ModelCallException(BusinessException):
    """Model invocation exception."""

    def __init__(self, message: str = "Model call error"):
        super().__init__(message, code="MODEL_CALL_ERROR", status_code=500)


class DuplicateResourceException(BusinessException):
    """Duplicate resource exception."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, code="DUPLICATE_RESOURCE", status_code=409)
