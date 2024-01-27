from fastapi import (
    FastAPI,
    Query,
    Depends,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from dependencies.db import get_db, engine
from api.users_routes import router as user_router
from api.auth_routes import router as auth_router
from models import user, client

from fastapi_limiter import FastAPILimiter

import redis.asyncio as redis
from conf.config import settings

user.Base.metadata.create_all(bind=engine)
client.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS:
allowed_sources = ["http://localhost:8001", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_sources,
    allow_credentials=True,
    allow_methods=["*"],  # all allowed
    allow_headers=["*"],  # all allowed
)

app.include_router(user_router, prefix="/users")
app.include_router(auth_router, prefix="/auth")


# Environment Variables section:
@app.on_event("startup")
async def startup():
    r = await redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(r)


@app.get("/")
def healthchecker(db: Session = Depends(get_db)):
    try:
        # Здійснюємо запит
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return "Database is configured correctly"
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
