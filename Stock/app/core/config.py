import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings:
    
    # 인증 서버 URL 설정
    AUTH_SERVER_URL: str = os.getenv("AUTH_SERVER_URL")
    
    # 오픈 API 키 설정
    OPEN_API_KEY: str = os.getenv("OPEN_API_KEY")
    
    # 해외 API 키 설정
    OVERSEA_API_KEY: str = os.getenv("OVERSEA_API_KEY")
    
    # 결과 파일 경로 설정
    RES_PATH: str = os.getenv("RES_PATH")
    
    # 토큰 파일 경로 설정
    TOKEN_FILE: str = os.getenv("TOKEN_FILE")
    OVERSEA_TOKEN_FILE: str = os.getenv("OVERSEA_TOKEN_FILE")
    
    # 도메인 설정
    DOMAIN: str = os.getenv("DOMAIN")
    
    # 웹소켓 URL 설정
    WEBSOCKET_URL: str = os.getenv("WEBSOCKET_URL")
    
    # 데이터베이스 설정
    SQLALCHEMY_DATABASE_URL: str = os.getenv("SQLALCHEMY_DATABASE_URL")
    
    # 앱 설정
    APP_NAME: str = os.getenv("APP_NAME")
    APP_VERSION: str = os.getenv("APP_VERSION")
    
    # CORS 설정
    CORS_ORIGINS: list = [
        "https://k2410.ebesesk.synology.me"
    ]
    
    # 레디스 설정
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT"))
    REDIS_DB: int = int(os.getenv("REDIS_DB"))

# 설정 인스턴스 생성
settings = Settings()