from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.db.base import Base

class Manga(Base):
    __tablename__ = "manga"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    folder_name = Column(Text, unique=True, index=True, nullable=False)
    tags = Column(Text, nullable=True)
    page = Column(Integer)
    images_name = Column(Text, nullable=True)
    create_date = Column(DateTime, nullable=True, default=datetime.utcnow)
    update_date = Column(DateTime, nullable=True, default=datetime.utcnow)
    file_date = Column(DateTime, nullable=True)
