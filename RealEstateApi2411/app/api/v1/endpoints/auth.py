from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.utils.dependencies import AuthClient
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.config import settings
from app.schemas.auth import LoginRequest, LoginResponse

router = APIRouter()
auth_client = AuthClient()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),):
    """로그인 처리"""
    print(form_data.username, form_data.password)
    username = form_data.username   
    password = form_data.password
    result = await auth_client.login(username, password)
    return result
    # try:
    #     # FastAPI202410 서버로 로그인 요청
    #     result = await auth_client.login(
    #         username=login_data.username,
    #         password=login_data.password
    #     )
    #     return result
    # except HTTPException as e:
    #     raise e
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=str(e)
    #     )

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """로그아웃 처리"""
    try:
        result = await auth_client.logout(token)
        return {"message": "로그아웃 성공"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )