"""Authentication schemas."""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
    user_id: str


class TokenPayload(BaseModel):
    sub: str
    exp: int


class UserInfo(BaseModel):
    id: str
    username: str
    email: str | None = None
    role: str
    status: str

    class Config:
        from_attributes = True
