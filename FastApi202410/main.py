from fastapi import FastAPI, Request
from app.api.api_v1.endpoints import users, auth
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["auth"]
)
app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["users"]
)

# @app.middleware("http")
# async def add_user_to_state(request: Request, call_next):
#     request.state.user = {"grade": 2}  # 예를 들면, grade 2를 가진 가짜 사용자 정보
#     response = await call_next(request)
#     return response