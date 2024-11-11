from fastapi import FastAPI, Request
from app.api.api_v1.endpoints import users, auth, manga, video
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from starlette.middleware.cors import CORSMiddleware
from app.db.session import init_db #db 초기화 
import logging

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# @app.on_event("startup")
# def on_startup():
#     init_db()  # 애플리케이션 시작 시 DB 초기화


origins = [
    # "http://localhost:1080",
    # "http://localhost:10443",
    # "http://192.168.0.43:1080", 
    # "http://191.168.0.43:10443",
    # "https://k202410.ebesesk.synology.me/",
    # "https://k202410api.ebesesk.synology.me/",
    # "https://ebesesk.synology.me/",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

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
app.include_router(
    manga.router,
    prefix=f"{settings.API_V1_STR}/manga",
    tags=["manga"]
)
app.include_router(
    video.router,
    prefix=f"{settings.API_V1_STR}/video",
    tags=["video"]
)






# 로깅 설정
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler(),  # 콘솔 출력
#         logging.FileHandler('manga_actions.log')  # 파일 출력
#     ]
# )
# @app.middleware("http")
# async def add_user_to_state(request: Request, call_next):
#     request.state.user = {"grade": 2}  # 예를 들면, grade 2를 가진 가짜 사용자 정보
#     response = await call_next(request)
#     return response