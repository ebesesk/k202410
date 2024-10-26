from sqlalchemy.orm import Session
from app.models.user import User, GradeEnum
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password
from fastapi import HTTPException
from typing import List, Optional

class UserCRUD:
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            grade=GradeEnum.BRONZE,
            points=0
        )
        db.add(db_user)
        try:
            db.commit()
            db.refresh(db_user)
        except Exception:
            db.rollback()
            raise HTTPException(status_code=400, detail="Username or email already exists")
        return db_user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update_user_points(db: Session, user: User, points: int) -> User:
        user.points += points
        user.grade = UserCRUD.calculate_grade(user.points)
        db.commit()
        return user

    @staticmethod
    def calculate_grade(points: int) -> GradeEnum:
        if points >= 1000:
            return GradeEnum.PLATINUM
        elif points >= 500:
            return GradeEnum.GOLD
        elif points >= 100:
            return GradeEnum.SILVER
        return GradeEnum.BRONZE