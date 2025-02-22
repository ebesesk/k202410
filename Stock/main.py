import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router  # api.py에서 라우터 임포트
from app.api.v2.api import api_router as v2_api_router # api.py에서 라우터 임포트
from app.api.dartutil.api import api_router as dart_api_router
# from app.api.v3.api import api_router as v3_api_router

from app.db.base import Base
from app.db.session import engine, investment_engine, asset_engine



    


# 앱 시작시 테이블 생성
# Base.metadata.create_all(bind=engine)
# Base.metadata.create_all(bind=investment_engine)
# Base.metadata.create_all(bind=asset_engine)

app = FastAPI(
    title="증권 API",
    description="증권 정보 제공 API",
    version="1.0.0",
    # root_path를 /stock로 설정
    root_path='/stock',
    # docs URL 경로 설정
    docs_url="/docs",
    # openapi.json URL 경로 설정
    openapi_url="/openapi.json"
)




# 모든 출처 허용 옵션
origins = [
    "https://k2410.ebesesk.synology.me",
    "https://k2410.ebesesk.synology.me/stock",
    "https://k2410.ebesesk.synology.me/stock/kis",
    "http://localhost:5173",
    "http://localhost:8000",
    # "http://api2410.ebesesk.synology.me"
    # "http://api2410.ebesesk.synology.me/stock",
    # "https://api2410.ebesesk.synology.me/users/me",
]

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    # allow_headers=["*"],
    allow_headers=[ 
            "Content-Type",
            "Accept",
            "X-API-KEY",
            "x-api-key",
            "Authorization",
            "Origin",
            "X-Requested-With",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers",
        ],
    expose_headers=["X-API-KEY"]
)

# API 라우터를 로 등록
app.include_router(api_router)
app.include_router(v2_api_router)
app.include_router(dart_api_router)
# app.include_router(v3_api_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        # host="0.0.0.0",
        port=8002,
        workers=1,
        reload=True
    )
