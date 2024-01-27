from sqlalchemy import Column, String, Boolean
from .base import BaseModel, Base


class ClientDB(BaseModel):
    __tablename__ = "clients_table"
    email = Column(String, unique=True)
    password = Column(String)
    refresh_token = Column(String)
    avatar = Column(String)
    confirmed = Column(Boolean, default=False)
