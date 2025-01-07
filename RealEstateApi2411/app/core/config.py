import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings:
    
    # 인증 서버 URL 설정
    AUTH_SERVER_URL: str = os.getenv("AUTH_SERVER_URL")
    
    # 공공포털 API 설정
    API_KEY: str = os.getenv("API_KEY")
    API_SERVER_URL: str = os.getenv("API_SERVER_URL")
    
    # 데이터베이스 설정
    SQLALCHEMY_DATABASE_URL: str = os.getenv("SQLALCHEMY_DATABASE_URL")
    
    # 앱 설정
    APP_NAME: str = os.getenv("APP_NAME")
    APP_VERSION: str = os.getenv("APP_VERSION")
    
    # CORS 설정
    CORS_ORIGINS: list = [
        "https://k2410.ebesesk.synology.me"
    ]

# 설정 인스턴스 생성
settings = Settings()