from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.db.session import Base

class Manga(Base):
    __tablename__ = "manga"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    folder_name = Column(Text, unique=True, index=True, nullable=False)
    tags = Column(Text, nullable=True)
    page = Column(Integer)
    images_name = Column(Text, nullable=True)
    create_date = Column(DateTime, nullable=True, default=datetime.now())
    update_date = Column(DateTime, nullable=True, default=datetime.now())
    file_date = Column(DateTime, nullable=True)

    # 추천 시스템을 위한 새로운 필드들
    rating_sum = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    rating_average = Column(Float, default=0.0)
    view_count = Column(Integer, default=0)
    
    # 관계 설정
    ratings = relationship("UserMangaRating", back_populates="manga")
    history = relationship("UserMangaHistory", back_populates="manga")
    
    def to_response(self):
        """MangaResponse 스키마에 맞는 딕셔너리 반환"""
        return {
            "id": self.id,
            "folder_name": self.folder_name,
            "images_name": self.images_name,
            "tags": self.tags,
            "page": self.page,
            "rating_average": self.rating_average,
            "user_rating": getattr(self, 'user_rating', None),
            "view_count": self.view_count,
            "create_date": self.create_date,
            "update_date": self.update_date
        }