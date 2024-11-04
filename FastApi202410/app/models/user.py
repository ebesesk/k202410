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

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    grade = Column(String, default=GradeEnum.BRONZE)
    is_active = Column(Boolean, default=True)
    points = Column(Integer, default=0)
    
    # 추천 시스템을 위한 관계 추가
    ratings = relationship("UserMangaRating", back_populates="user", cascade="all, delete-orphan")
    history = relationship("UserMangaHistory", back_populates="user", cascade="all, delete-orphan")