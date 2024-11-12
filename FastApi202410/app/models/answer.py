from sqlalchemy import (Column, Integer, String, Text, DateTime, 
                        ForeignKey, Boolean, Date, Table, MetaData)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.db.session import Base



class Answer(Base):
    __tablename__ = "answer"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    create_date = Column(DateTime, nullable=False)
    question_id = Column(Integer, ForeignKey("question.id"))
    question = relationship("Question", back_populates="answers")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="user_answers")  # 변경된 부분
    modify_date = Column(DateTime, nullable=True)