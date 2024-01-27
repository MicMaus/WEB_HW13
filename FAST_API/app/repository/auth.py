from sqlalchemy.orm import Session

from models.client import ClientDB
from schemas.client import ClientPydant
from conf.config import settings


def get_user_by_email(email: str, db: Session) -> ClientDB:
    return db.query(ClientDB).filter(ClientDB.email == email).first()


def create_user(body: ClientPydant, db: Session) -> ClientDB:
    new_user = ClientDB(**body.dict(), avatar=settings.avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_token(user: ClientDB, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()


# function will set attribute "confirmed" to True in db.
def confirmed_email(email: str, db: Session) -> None:
    user = get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


def update_avatar_in_database(db: Session, user_id: int, new_avatar_url: str):
    user = db.query(ClientDB).filter(ClientDB.id == user_id).first()
    user.avatar = new_avatar_url
    db.commit()
    db.refresh(user)
    return user
