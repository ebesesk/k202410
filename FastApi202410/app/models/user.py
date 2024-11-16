from sqlalchemy import Column, Integer, String, Enum, Boolean, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
import enum
from app.db.session import Base
from datetime import datetime

class GradeEnum(str, enum.Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    grade = Column(String, default=GradeEnum.BRONZE)
    points = Column(Integer, default=0)
    user_questions = relationship("Question", back_populates="user")   # 변경된 부분
    user_answers = relationship("Answer", back_populates="user")
    # 추천 시스템을 위한 관계 추가
    ratings = relationship("UserMangaRating", back_populates="user", cascade="all, delete-orphan")
    history = relationship("UserMangaHistory", back_populates="user", cascade="all, delete-orphan")
    video_ratings = relationship("VideoRating", back_populates="user")