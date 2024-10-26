from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionLocal
from app.crud.user import UserCRUD
from app.schemas.user import TokenData
from app.schemas.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> UserCRUD:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = UserCRUD.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_user_with_grade(required_points: int):
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
        ):
        # 데이터베이스에서 최신 사용자 정보를 가져옵니다.
        db_user = UserCRUD.get_user(db, current_user.id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        current_points = db_user.points
        if current_points < required_points:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return db_user
    return dependency