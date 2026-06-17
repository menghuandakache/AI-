"""Standardized API response utilities."""


def success_response(data=None, message: str = "ok") -> dict:
    """Create a standard success response."""
    return {
        "code": "SUCCESS",
        "message": message,
        "data": data,
    }


def paginated_response(items: list, total: int, page: int, page_size: int) -> dict:
    """Create a standard paginated response."""
    return {
        "code": "SUCCESS",
        "message": "ok",
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }


def error_response(code: str, message: str) -> dict:
    """Create a standard error response."""
    return {
        "code": code,
        "message": message,
        "data": None,
    }
