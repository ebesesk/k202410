from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "user@example.com",
                "password": "userpassword123"
            }
        }

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    userpoints: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "username": "username",
                "userpoints": 100
            }
        }

class LogoutResponse(BaseModel):
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "로그아웃 성공"
            }
        }

class TokenData(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None