from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.crud.user import UserCRUD
from app.schemas.user import UserCreate, UserResponse
from app.utils.dependencies import (
    get_db,
    get_current_user,
    get_current_active_user,
    get_current_user_with_grade
)
from app.models.user import GradeEnum, User
from starlette import status

router = APIRouter()

@router.post("", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return UserCRUD.create_user(db, user)

@router.get("", response_model=List[UserResponse])
def get_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_grade(1000)),
    ):
    return UserCRUD.get_users(db, skip=skip, limit=limit)

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ):
    """
    현재 로그인한 사용자의 정보를 반환
    """
    print(current_user)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = UserCRUD.get_user(db, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = UserCRUD.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}/add-points")
def add_points(
    user_id: int, 
    points: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_grade(1000)),
    ):
    
    # current_user: User = Depends(get_current_user_with_grade(500))
    print(current_user.id)
    
    user = UserCRUD.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = UserCRUD.update_user_points(db, user, points)
    return {
        "message": f"Added {points} points. New total: {updated_user.points}, New grade: {updated_user.grade}"
    }

@router.get("/{user_id}/grade")
def get_user_grade(user_id: int, db: Session = Depends(get_db)):
    user = UserCRUD.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    next_grade_info = {
        GradeEnum.BRONZE: f"{100 - user.points} points to SILVER",
        GradeEnum.SILVER: f"{500 - user.points} points to GOLD",
        GradeEnum.GOLD: f"{1000 - user.points} points to PLATINUM",
        GradeEnum.PLATINUM: "Maximum grade reached"
    }[user.grade]

    return {
        "username": user.username,
        "grade": user.grade,
        "points": user.points,
        "next_grade": next_grade_info,
        "is_active": user.is_active
    }
    
