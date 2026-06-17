"""API dependencies - injected by routes."""
from app.core.database import SessionLocal


def get_db():
    """Provide database session for API routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
