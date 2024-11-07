from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MangaBase(BaseModel):
    """
    망가 기본 스키마 - 공통 속성 정의
    
    Attributes:
        folder_name (str): 망가 폴더명
        tags (Optional[str]): 망가 태그들
        page (int): 페이지 수
        images_name (Optional[str]): 이미지 파일명들
    """
    folder_name: str
    tags: Optional[str] = None
    page: int
    images_name: Optional[str] = None
    

class MangaCreate(MangaBase):
    """망가 생성을 위한 스키마"""
    file_date: Optional[datetime] = None

class MangaUpdate(BaseModel):
    """
    망가 업데이트를 위한 스키마
    모든 필드를 선택적으로 만듦
    """
    folder_name: str
    tags: Optional[str] = None
    page: int 
    images_name: Optional[str] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    file_datee: Optional[datetime] = None

# class MangaBulkCreate

    
class Manga(MangaBase):
    """
    API 응답에서 사용할 망가 스키마
    
    Attributes:
        id (int): 데이터베이스 ID
        create_date (datetime): 생성 일시
        update_date (datetime): 수정 일시
        file_date (Optional[datetime]): 파일 날짜
    """
    id: int
    create_date: datetime
    update_date: datetime
    file_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class MangaResponse(BaseModel):
    id: int
    folder_name: str
    images_name: Optional[str] = None
    tags: Optional[str] = None
    page: Optional[int] = None
    rating_average: float = 0.0
    user_rating: Optional[float] = None
    view_count: int = 0
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PaginatedMangaResponse(BaseModel):
    """
    페이지네이션된 망가 목록 응답 스키마
    
    Attributes:
        items (List[Manga]): 현재 페이지의 망가 목록
        total (int): 전체 망가 수
        page (int): 현재 페이지 번호
        size (int): 페이지당 아이템 수
        pages (int): 전체 페이지 수
    """
    items: List[MangaResponse]
    total: int
    page: int
    size: int
    pages: int
    genres: Optional[List[str]] = None


class MangaActionRequest(BaseModel):
    manga_ids: List[int]
    target_folder_name: str
    action: str
    
class MangafolderName(BaseModel):
    id: int
    folder_name: str
    
    class Config:
        from_attributes = True