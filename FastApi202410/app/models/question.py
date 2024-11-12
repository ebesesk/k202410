from sqlalchemy import (Column, Integer, String, Text, DateTime, 
                        ForeignKey, Boolean, Date, Table, MetaData)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.db.session import Base



class Question(Base):
    __tablename__ = "question"

    id = Column(Integer, primary_key=True)
    subject = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    create_date = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="user_questions")  # 변경된 부분
    modify_date = Column(DateTime, nullable=True)
    
    # Answer와의 관계 추가
    answers = relationship("Answer", back_populates="question")  # 추가된 부분