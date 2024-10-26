from sqlalchemy import Column, Integer, String, Enum
import enum
from app.db.base import Base

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
    points = Column(Integer, default=0)