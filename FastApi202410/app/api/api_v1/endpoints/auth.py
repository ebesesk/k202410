from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.config import settings
from app.core.security import create_access_token
from app.crud.user import UserCRUD
from app.utils.dependencies import get_db, get_current_active_user
from app.schemas.user import Token, User

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = UserCRUD.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    UserCRUD.update_user_status(db, user.id, True)  # 로그인 시 is_active를 True로 설정
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout_user(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    UserCRUD.update_user_status(db, current_user.id, False)  # 로그아웃 시 is_active를 False로 설정
    return {"message": "Successfully logged out"}