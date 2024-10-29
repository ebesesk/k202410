from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.config import settings
from app.core.security import create_access_token
from app.crud.user import UserCRUD
from app.utils.dependencies import get_db, get_current_active_user
from app.schemas.user import Token, User
from app.core.security import verify_jwt_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# 로그인
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
    return {"access_token": access_token, 
            "token_type": "bearer",
            "username": user.username,
            "userpoints": user.points}

@router.post("/logout")
def logout_user(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    UserCRUD.update_user_status(db, current_user.id, False)  # 로그아웃 시 is_active를 False로 설정
    return {"message": "Successfully logged out"}


# nginx 파일서버 인증
@router.get("/nginxauth")
async def auth_jwt(request: Request):
    auth_header = request.headers.get("Authorization")
    # print(auth_header)
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else ""
    # print(token)
    verify_jwt_token(token)
    # print("nginxauth: ", token, '////////')
    return {"status": "ok"}  # 성공 시 200 상태 코드 반환
    