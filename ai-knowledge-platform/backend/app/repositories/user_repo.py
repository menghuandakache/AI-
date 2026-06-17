"""User repository for database operations."""
from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def create(self, username: str, password_hash: str, email: str = None, role: str = "user") -> User:
        user = User(
            username=username,
            password_hash=password_hash,
            email=email,
            role=role,
            status="active",
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_status(self, user_id: str, status: str) -> User | None:
        user = self.get_by_id(user_id)
        if user:
            user.status = status
            self.db.commit()
            self.db.refresh(user)
        return user

    def list_users(self, page: int = 1, page_size: int = 20) -> list[User]:
        return self.db.query(User).order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    def count_users(self) -> int:
        return self.db.query(User).count()
