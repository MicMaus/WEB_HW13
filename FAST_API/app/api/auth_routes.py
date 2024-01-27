from schemas.client import ClientPydant, TokenPydant, ClientUpdatePydant
from schemas.verificaiton_email import RequestEmail
from repository import auth as repository_auth
from fastapi import (
    HTTPException,
    status,
    Security,
    Depends,
    APIRouter,
    Security,
    BackgroundTasks,
    Request,
)

from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from services.auth import (
    verify_password,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    decode_refresh_token,
    get_email_from_token,
    get_connected_client,
)
from services.users import UserService
from sqlalchemy.orm import Session
from dependencies.db import get_db, SessionLocal

from schemas.client import ClientPydant, ClientResponsePydant

from services.verification_email import send_email


router = APIRouter()  # tags=["auth"]
security = HTTPBearer()


@router.post(
    "/signup", response_model=ClientResponsePydant, status_code=status.HTTP_201_CREATED
)
def signup(
    body: ClientPydant,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    exist_user = repository_auth.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = get_password_hash(body.password)
    new_user = repository_auth.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, request.base_url.hostname)
    return {
        "user": new_user,
        "detail": "User successfully created. Check your email for confirmation.",
    }


@router.put(
    "/{id}", response_model=ClientResponsePydant, status_code=status.HTTP_201_CREATED
)
def update_client(
    id: int,
    todo_item: ClientUpdatePydant,
    db: SessionLocal = Depends(get_db),
    # current_user: str = Depends(get_connected_client),
) -> ClientPydant:
    updated_client = UserService(db=db).update_existing(id, todo_item)
    return {"user": updated_client, "detail": "Client successfully updated"}


# @router.put(
#     "/{id}", response_model=ClientResponsePydant, status_code=status.HTTP_201_CREATED
# )
# def update_client(
#     id: int,
#     todo_item: ClientUpdatePydant,
#     db: SessionLocal = Depends(get_db),
#     # current_user: str = Depends(get_connected_client),
# ) -> ClientPydant:
#     updated_client = UserService(db=db).update_existing(id, todo_item)
#     return updated_client


@router.post("/login", response_model=TokenPydant)
def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = repository_auth.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )
    if not verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    # Generate JWT
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    repository_auth.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", response_model=TokenPydant)
def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    email = decode_refresh_token(token)
    user = repository_auth.get_user_by_email(email, db)
    if user.refresh_token != token:
        repository_auth.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = create_access_token(data={"sub": email})
    refresh_token = create_refresh_token(data={"sub": email})
    repository_auth.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = get_email_from_token(token)
    user = repository_auth.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    repository_auth.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    user = repository_auth.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Check your email for confirmation."}
