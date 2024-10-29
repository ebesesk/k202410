from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.utils.dependencies import get_db, get_current_user_with_grade, get_current_user
from app.schemas.manga import MangaCreate, PaginatedMangaResponse
# from app.crud.manga import create_manga#, get_manga_list
from app.utils.manga import list_images_from_folders
from app.crud.manga import MangaCRUD
from app.core.config import settings
from typing import Optional
from math import ceil

router = APIRouter()

@router.post("/bulk-insert")
def bulk_insert_manga(
    base_folder_path: str=settings.IMAGE_DIRECTORY, 
    db: Session = Depends(get_db)
    ):
    
    manga_data = list_images_from_folders(base_folder_path)
    
    # import pickle
    # with open('manga_data.pkl', 'wb') as f:
    #     pickle.dump(manga_data, f)
    
    # corrupt_images = []
    # for i, manga in enumerate(manga_data):
    #     try:
    #         MangaCRUD.create_manga(db, manga)
    #     except Exception as e:
    #         print(f"{i} Error inserting manga: {manga['folder_name']}: {e}")
    #         corrupt_images.append(manga)
            
    # MangaCRUD.bulk_update_manga(db, manga_data)     # update
    MangaCRUD.bulk_insert_manga(db, manga_data)   # insert
    return {"detail": "Bulk insert successful"}

@router.get("/mangas/", response_model=PaginatedMangaResponse)
def read_mangas(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지당 아이템 수"),
    sort_by: str = Query("id", description="정렬 기준 필드"),
    order: str = Query("desc", description="정렬 방향 (asc/desc)"),
    search: Optional[str] = Query(None, description="검색어")
):
    """
    페이지네이션된 망가 목록을 조회하는 API 엔드포인트
    """
    skip = (page - 1) * size
    
    mangas = MangaCRUD.get_mangas_with_pagination(
        db,
        skip=skip,
        limit=size,
        sort_by=sort_by,
        order=order,
        search=search
    )
    
    total = MangaCRUD.get_total_manga_count(db, search=search)
    total_pages = ceil(total / size)
    
    return PaginatedMangaResponse(
        items=mangas,
        total=total,
        page=page,
        size=size,
        pages=total_pages
    )