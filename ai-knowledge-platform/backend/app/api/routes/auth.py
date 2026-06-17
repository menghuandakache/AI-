"""Authentication routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth_service import AuthService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """User login endpoint."""
    service = AuthService(db)
    return service.login(request.username, request.password)


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user info."""
    service = AuthService(db)
    return service.get_current_user_info(str(current_user.id))


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """User logout (client-side token removal)."""
    return {"message": "Logged out successfully"}
