from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.config import settings
from app.core.security import create_access_token
from app.crud.user import UserCRUD
from app.schemas.user import Token, User
from app.core.security import verify_jwt_token

from app.utils.dependencies import (
    get_db,
    get_current_user,
    get_current_active_user
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# 로그인
@router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
    ):
    print(form_data.username, form_data.password)
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
            "userpoints": user.points,}

@router.post("/logout")
def logout_user(db: Session = Depends(get_db),
                current_user: User = Depends(get_current_active_user), 
                ):
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

@router.get("/verify", response_model=User)
async def verify_token(token: str = Depends(oauth2_scheme),
                      db: Session = Depends(get_db)):
    """토큰 검증 엔드포인트"""

    payload =verify_jwt_token(token)
    print(payload)
    username: str = payload.get("sub")
    user = UserCRUD.get_user_by_username(db, username=username)
    # 사용자 정보 반환
    return user

# 비밀번호 변경 
@router.post("/change_password")
async def change_password(
        current_password: str,
        new_password: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
    ):
    try:
        # 현재 비밀번호 확인
        user = UserCRUD.authenticate_user(
            db, 
            current_user.username, 
            current_password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="현재 비밀번호가 일치하지 않습니다"
            )
        
        # 새 비밀번호로 업데이트
        UserCRUD.change_password(db, user.id, new_password)
        
        return {"message": "비밀번호가 성공적으로 변경되었습니다"}
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"비밀번호 변경 실패: {str(e)}"
        )
        
# 비밀번호 재설정
@router.post("/reset_password")
async def reset_password(
        username: str,
        new_password: str,
        admin_password: str,  # 관리자 비밀번호로 인증
        # current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
    # print(current_user.points, current_user.username)
    try:
        # 관리자 인증
        admin = UserCRUD.authenticate_user(
            db, 
            "kds",  # 관리자 계정명 
            admin_password
        )
        
        if not admin or not admin.username == "kds" or username == "kds" or admin.points < 2000:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="관리자 인증 실패"
            )
        
        # 사용자 존재 확인
        user = UserCRUD.get_user_by_username(db, username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다"
            )
        
        # 새 비밀번호로 업데이트
        UserCRUD.change_password(db, user.id, new_password)
        
        return {"message": "비밀번호가 성공적으로 재설정되었습니다"}
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"비밀번호 재설정 실패: {str(e)}"
        )