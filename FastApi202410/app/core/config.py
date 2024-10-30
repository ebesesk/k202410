from pydantic_settings import BaseSettings
from datetime import timedelta

class Settings(BaseSettings):
    # API_V1_STR: str = "/api/v1"
    API_V1_STR: str = ""
    PROJECT_NAME: str = "User Grade System"
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./K202410.db"
    SECRET_KEY: str = "your-secret-key-here"  # 실제 운영환경에서는 안전한 키로 변경
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 600
    IMAGE_DIRECTORY: str = "/home/manga"
    
    class Config:
        case_sensitive = True

settings = Settings()