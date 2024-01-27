from pydantic import BaseModel, PastDate, EmailStr, constr, Field
from typing import Optional
from models.user import UserDB
from dependencies.db import get_db, SessionLocal
from fastapi import Depends

SessionLocal = Depends(get_db)


class UserPydant(BaseModel):
    id: int
    name: str
    surname: str
    email: EmailStr
    phone: constr(pattern=r"^\+?[1-9]\d{8,14}$")
    birthday: PastDate
    additional_description: str | None
    # not mandatory field, but 'None' needs to be received from frontend!

    # for proper converting to sql alchem model:
    class Config:
        orm_mode = True
        from_orm = True
        from_attributes = True


class UserUpdatePydant(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[constr(pattern=r"^\+?[1-9]\d{8,14}$")] = None
    birthday: Optional[PastDate] = None
    additional_description: Optional[str] = None
