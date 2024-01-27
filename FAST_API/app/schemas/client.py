from pydantic import BaseModel, EmailStr
from typing import Optional


class ClientPydant(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True
        from_orm = True
        from_attributes = True


class ClientResponsePydant(BaseModel):
    user: ClientPydant
    detail: str


class ClientUpdatePydant(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    avatar: Optional[str] = None


class TokenPydant(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
