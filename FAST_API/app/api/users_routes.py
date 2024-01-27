from fastapi import APIRouter, Depends
from schemas.user import UserPydant, UserUpdatePydant
from dependencies.db import get_db, SessionLocal
from services.users import UserService
from services.auth import get_connected_client

from fastapi_limiter.depends import RateLimiter

router = APIRouter()


@router.get(
    "/",
    description="No more than 5 requests each 20 sec",
    dependencies=[Depends(RateLimiter(times=5, seconds=20))],
)
def list_users(db: SessionLocal = Depends(get_db)) -> list[UserPydant]:
    todo_items = UserService(db=db).get_all_users()
    return todo_items


@router.get(
    "/upcoming-birthdays",
    description="No more than 5 requests each 20 sec",
    dependencies=[Depends(RateLimiter(times=5, seconds=20))],
)
def get_upcoming_birthdays(db: SessionLocal = Depends(get_db)):
    return UserService(db).get_upcoming_birthdays()


@router.get(
    "/{id}",
    description="No more than 5 requests each 20 sec",
    dependencies=[Depends(RateLimiter(times=5, seconds=20))],
)
def get_detail(id: int, db: SessionLocal = Depends(get_db)) -> UserPydant:
    todo_item = UserService(db=db).get_by_id(id)
    return todo_item


@router.post(
    "/",
    description="No more than 5 requests each 20 sec",
    dependencies=[Depends(RateLimiter(times=5, seconds=20))],
)
def create_user(
    todo_item: UserPydant,
    db: SessionLocal = Depends(get_db),
    current_user: str = Depends(get_connected_client),
) -> UserPydant:
    new_item = UserService(db=db).create_new(todo_item)
    return new_item


@router.put(
    "/{id}",
    description="No more than 5 requests each 20 sec",
    dependencies=[Depends(RateLimiter(times=5, seconds=20))],
)
def update_user(
    id: int,
    update_data: UserUpdatePydant,
    db: SessionLocal = Depends(get_db),
    current_user: str = Depends(get_connected_client),
) -> UserPydant:
    updated_user = UserService(db=db).update_existing(id, update_data)
    return updated_user


@router.delete(
    "/{id}",
    description="No more than 5 requests each 20 sec",
    dependencies=[Depends(RateLimiter(times=5, seconds=20))],
)
def delete_user(
    id: int,
    db: SessionLocal = Depends(get_db),
    current_user: str = Depends(get_connected_client),
):
    UserService(db=db).delete_by_id(id)
    return f"message: User {id} was deleted"


@router.get(
    "/search/{query}",
    description="No more than 5 requests each 20 sec",
    dependencies=[Depends(RateLimiter(times=5, seconds=20))],
)
# optionally this method can be moved to the top before other methods with "/{id}", in such case {query} can be removed from this decorator. now {query} serves to avoid conflicts
def search_users(query: str, db: SessionLocal = Depends(get_db)):
    return UserService(db).search(query)
