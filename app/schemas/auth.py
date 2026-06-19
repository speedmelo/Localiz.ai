from datetime import datetime

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime | None = None


class TokenPayload(BaseModel):
    sub: str
    email: EmailStr | None = None
    exp: int | None = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
