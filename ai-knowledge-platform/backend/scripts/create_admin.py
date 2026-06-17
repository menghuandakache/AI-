"""Create an admin user."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.core.config import get_settings
from app.repositories.user_repo import UserRepository

settings = get_settings()


def create_admin():
    """Create default admin user if not exists."""
    db = SessionLocal()
    try:
        repo = UserRepository(db)
        existing = repo.get_by_username(settings.DEFAULT_ADMIN_USERNAME)
        if existing:
            print(f"Admin user '{settings.DEFAULT_ADMIN_USERNAME}' already exists.")
            return

        repo.create(
            username=settings.DEFAULT_ADMIN_USERNAME,
            password_hash=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
            email=settings.DEFAULT_ADMIN_EMAIL,
            role="admin",
        )
        print(f"Admin user '{settings.DEFAULT_ADMIN_USERNAME}' created successfully!")
        print(f"Password: {settings.DEFAULT_ADMIN_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
