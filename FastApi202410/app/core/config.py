from pydantic_settings import BaseSettings
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    # API_V1_STR: str = "/api/v1"
    API_V1_STR: str = ""
    PROJECT_NAME: str = "User Grade System"
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./K202410.db"
    SECRET_KEY: str = "your-secret-key-here"  # 실제 운영환경에서는 안전한 키로 변경
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 600
    IMAGE_DIRECTORY: str = "/home/manga"
    VIDEO_DIRECTORY: str = "/home/video"
    
    MANGA_DIR: str | None = os.environ.get("MANGA_DIR")
    MANGA_DIR2: str | None = os.environ.get("MANGA_DIR2")
    MANGA_HTTP: str | None = os.environ.get("MANGA_HTTP")
    VIDEO_DIR: str | None    = os.environ.get("VIDEO_DIR")
    TEMP_DIR: str | None = os.environ.get("TEMP_DIR")
    GIF_FRAMES_MIN: int | None = int(os.environ.get("GIF_FRAMES_MIN"))
    GIF_FRAMES_MAX: int | None = int(os.environ.get("GIF_FRAMES_MAX"))
    GIF_SIZE: int | None = int(os.environ.get("GIF_SIZE"))
    WASTE_DIR: str | None = os.environ.get("WASTE_DIR")
    
    
    class Config:
        case_sensitive = True

settings = Settings()