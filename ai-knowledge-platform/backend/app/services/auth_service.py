"""Authentication service."""
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import BusinessException
from app.repositories.user_repo import UserRepository

settings = get_settings()


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def login(self, username: str, password: str) -> dict:
        """Authenticate user and return JWT token."""
        user = self.user_repo.get_by_username(username)
        if not user:
            raise BusinessException("Invalid username or password", code="AUTH_ERROR", status_code=401)

        if user.status != "active":
            raise BusinessException("Account is inactive", code="AUTH_ERROR", status_code=403)

        if not verify_password(password, user.password_hash):
            raise BusinessException("Invalid username or password", code="AUTH_ERROR", status_code=401)

        access_token = create_access_token(data={"sub": str(user.id)})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "username": user.username,
            "role": user.role,
            "user_id": str(user.id),
        }

    def get_current_user_info(self, user_id: str) -> dict:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise BusinessException("User not found", code="NOT_FOUND", status_code=404)
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "status": user.status,
        }
