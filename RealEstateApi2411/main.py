from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router  # api.py에서 라우터 임포트

from app.db.base import Base
from app.db.session import engine


# 앱 시작시 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="아파트 실거래가 API",
    description="아파트 매매 실거래가 정보 제공 API",
    version="1.0.0",
    # root_path를 /realestate로 설정
    root_path='/realestate',
    # docs URL 경로 설정
    docs_url="/docs",
    # openapi.json URL 경로 설정
    openapi_url="/openapi.json"
)

# 모든 출처 허용 옵션
origins = [
    "https://k2410.ebesesk.synology.me",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://api2410.ebesesk.synology.me"
    "http://api2410.ebesesk.synology.me/realestate",
]

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터를 로 등록
app.include_router(api_router)