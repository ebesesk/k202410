from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base
from datetime import datetime

class UserMangaRating(Base):
    __tablename__ = "user_manga_ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    manga_id = Column(Integer, ForeignKey("manga.id"))
    rating = Column(Float)  # 1-5점 평점
    created_at = Column(DateTime, default=datetime.now())
    
    user = relationship("User", back_populates="ratings")
    manga = relationship("Manga", back_populates="ratings")

class UserMangaHistory(Base):
    __tablename__ = "user_manga_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    manga_id = Column(Integer, ForeignKey("manga.id"))
    view_count = Column(Integer, default=1)
    last_viewed = Column(DateTime, default=datetime.now())
    
    user = relationship("User", back_populates="history")
    manga = relationship("Manga", back_populates="history")