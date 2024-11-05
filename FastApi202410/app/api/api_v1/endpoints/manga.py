from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.utils.dependencies import get_db, get_current_user_with_grade, get_current_user
from app.schemas.manga import MangaCreate, PaginatedMangaResponse
# from app.crud.manga import create_manga#, get_manga_list
from app.utils.manga import list_images_from_folders, get_genres_list
from app.crud.manga import MangaCRUD
from app.crud.rating import RatingCRUD
from app.core.config import settings
from app.schemas.rating import RatingCreate  # 추가
from typing import Optional, List
from math import ceil
from app.models.user import User
router = APIRouter()

@router.post("/bulk-insert")
def bulk_insert_manga(
    base_folder_path: str=settings.IMAGE_DIRECTORY, 
    db: Session = Depends(get_db)
    ):
    
    manga_data = list_images_from_folders(base_folder_path)            
    MangaCRUD.bulk_insert_manga(db, manga_data)   # insert
    return {"detail": "Bulk insert successful"}

@router.post("/bulk-update")
def bulk_update_manga(
    base_folder_path: str=settings.IMAGE_DIRECTORY, 
    db: Session = Depends(get_db)
    ):
    
    manga_data = list_images_from_folders(base_folder_path)      # 파일시스템의 망가 데이터 조회
    remaining_mangas = MangaCRUD.bulk_update_manga(db, manga_data)     # 데이터베이스의 망가 데이터 업데이트
    print('update remaining_mangas:', len(remaining_mangas))
    _insert = MangaCRUD.bulk_insert_manga(db, remaining_mangas)     # 데이터베이스에 망가 데이터 삽입
    print('insert:', len(_insert))
    delete_count = MangaCRUD.bulk_delete_nonexistent_manga(db, manga_data) # 파일시스템에 존재하지 않는 망가 데이터 삭제
    print('bulk_delete:', delete_count)
    return {"detail": "Bulk update successful"}


@router.get("/mangas/", response_model=PaginatedMangaResponse)
def read_mangas(
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user),  # 현재 사용자 정보 추가
        page: int = Query(1, ge=1, description="페이지 번호"),
        size: int = Query(10, ge=1, le=100, description="페이지당 아이템 수"),
        sort_by: str = Query("id", description="정렬 기준 필드"),
        order: str = Query("desc", description="정렬 방향 (asc/desc)"),
        search: Optional[str] = Query(None, description="검색어"),
        folders: Optional[List[str]] = Query(None, description="활성화된 폴더 목록")
    ):
    """
    페이지네이션된 망가 목록을 조회하는 API 엔드포인트
    
    - sort_by: 정렬 기준 (id, rating, create_date, update_date)
    - order: 정렬 방향 (asc, desc)
    """
    # 허용된 정렬 필드 검증
    allowed_sort_fields = ["id", "rating", "create_date", "update_date"]
    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by field. Allowed values are: {', '.join(allowed_sort_fields)}"
        )
    
    # 허용된 정렬 방향 검증
    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid order value. Must be either 'asc' or 'desc'"
        )
    
    skip = (page - 1) * size
    
    mangas = MangaCRUD.get_mangas_with_pagination(
        db,
        skip=skip,
        limit=size,
        sort_by=sort_by,
        order=order,
        search=search,
        user_id=current_user.id if current_user else None,
        folders=folders
    )
    
    total = MangaCRUD.get_total_manga_count(
        db, 
        search=search,
        folders=folders
    )
    
    total_pages = ceil(total / size)
    genres = get_genres_list()
    print(PaginatedMangaResponse(
            items=mangas,
            total=total,
            page=page,
            size=size,
            pages=total_pages,
            genres=genres
        ))
    return PaginatedMangaResponse(
        items=mangas,
        total=total,
        page=page,
        size=size,
        pages=total_pages,
        genres=genres
    )
    
    
@router.post("/{manga_id}/rate")
def rate_manga(
        manga_id: int,
        rating_data: RatingCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
    """망가에 평점을 부여합니다."""
    manga = MangaCRUD.get_manga_by_id(db, manga_id)
    if not manga:
        raise HTTPException(status_code=404, detail="Manga not found")
    
    rating = RatingCRUD.add_or_update_rating(
        db, current_user.id, manga_id, rating_data.rating
    )
    return {"message": "Rating added successfully"}

@router.delete("/{manga_id}/rate")  # DELETE 엔드포인트 추가
def delete_manga_rating(
        manga_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
    """망가의 평점을 삭제합니다."""
    manga = MangaCRUD.get_manga_by_id(db, manga_id)
    if not manga:
        raise HTTPException(status_code=404, detail="Manga not found")
    
    success = RatingCRUD.delete_rating(db, current_user.id, manga_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rating not found")
        
    return {"message": "Rating deleted successfully"}

@router.post("/{manga_id}/view")
def record_view(
        manga_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
    """망가 조회 기록을 저장합니다."""
    manga = MangaCRUD.get_manga_by_id(db, manga_id)
    if not manga:
        raise HTTPException(status_code=404, detail="Manga not found")
    
    RatingCRUD.add_view_history(db, current_user.id, manga_id)
    return {"message": "View recorded successfully"}


@router.get("/user-ratings/")
def get_user_ratings(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
    """현재 사용자의 모든 평점을 반환합니다."""
    ratings = RatingCRUD.get_user_ratings(db, current_user.id)
    
    return ratings

@router.get("/recommended/")
def get_recommended_mangas(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
    """사용자를 위한 추천 망가 목록을 반환합니다."""
    recommended = RatingCRUD.get_recommended_mangas(db, current_user.id)
    
    return recommended