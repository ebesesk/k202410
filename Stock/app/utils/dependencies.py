from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import OAuth2PasswordBearer
import requests
from app.core.config import settings
from app.db.session import SessionLocal
from typing import Generator


# 인증 서버 URL 설정
AUTH_SERVER_URL = settings.AUTH_SERVER_URL  # 실제 서버 URL로 변경 필요
# OAuth2 스키마 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{AUTH_SERVER_URL}/auth/login")


# DB 의존성
from app.db.session import investment_session
def get_investment_db():
    db = investment_session()
    try:
        yield db
    finally:
        db.close()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AuthClient:
    def __init__(self):
        self.auth_server_url = AUTH_SERVER_URL
        self.login_url = f"{self.auth_server_url}/auth/login"
        self.logout_url = f"{self.auth_server_url}/auth/logout"
        self.verify_url = f"{self.auth_server_url}/auth/verify"
        
    async def login(self, username: str, password: str):
        """로그인 요청"""
        try:
            login_data = {
                "username": username,
                "password": password
            }
            print(self.login_url, 'login_url')
            response = requests.post(
                self.login_url,
                data=login_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="로그인 실패: " + response.text
                )
                
        except requests.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"인증 서버 연결 실패: {str(e)}"
            )
    
    async def logout(self, token: str):
        """로그아웃 요청"""
        try:
            response = requests.post(
                self.logout_url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="로그아웃 실패: " + response.text
                )
                
        except requests.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"인증 서버 연결 실패: {str(e)}"
            )

    async def verify_token(self, token: str):
        """토큰 검증"""
        try:
            response = requests.get(
                self.verify_url,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="인증되지 않은 사용자입니다",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
        except requests.RequestException:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="인증 서버에 연결할 수 없습니다"
            )

    async def get_current_user(self, token: str = Depends(oauth2_scheme)):
        """현재 사용자 정보 조회"""
        return await self.verify_token(token)


# 싱글톤 인스턴스 생성
auth_client = AuthClient()

# 의존성 함수
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """현재 사용자 정보를 반환하는 의존성"""
    return await auth_client.get_current_user(token)

# 웹소켓 연결을 위한 토큰 검증
async def verify_ws_token(websocket: WebSocket, token: str = None):
    """WebSocket 연결을 위한 토큰 검증"""
    # token = websocket.headers.get('token')
    # protocols = websocket.headers.get('sec-websocket-protocol', '').split(', ')
    # token = next((p.split('.')[1] for p in protocols if p.startswith('token.')), None)
    # print('verify_ws_token:', token)
    try:
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None
            
        user = await auth_client.verify_token(token)
        return user
        
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None
    except Exception as e:
        print(f"WebSocket 인증 오류: {str(e)}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None


async def verify_token(token: str):
    """토큰 검증 함수"""
    try:
        # 여기에 실제 토큰 검증 로직 구현
        user = await auth_client.verify_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )