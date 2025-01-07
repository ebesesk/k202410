from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.utils.dependencies import (
    get_db,
    get_current_user_with_grade,
    get_current_user
)
from app.schemas.manga import MangaCreate, PaginatedMangaResponse
# from app.crud.manga import create_manga#, get_manga_list
from app.utils.manga import list_images_from_folders, get_genres_list, move_manga_folder, merge_manga_folder
from app.crud.manga import MangaCRUD
from app.crud.rating import RatingCRUD
from app.core.config import settings
from app.schemas.rating import RatingCreate
from app.schemas.manga import MangaActionRequest, MangafolderName
from typing import Optional, List, Dict, Any
from math import ceil
from app.models.user import User
import os
import logging
import traceback
from datetime import datetime
import time

router = APIRouter()
# 로거 설정
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

@router.post("/bulk-update")    # 파일시스템의 망가 데이터를 데이터베이스에 업데이트 합니다.
def bulk_update_manga(
    genre_name: str = '', 
    db: Session = Depends(get_db)
    ):
    # print('bulk_update_manga:', genre_name)
    manga_data = list_images_from_folders(genre_name)      # 파일시스템의 망가 데이터 조회
    remaining_mangas = MangaCRUD.bulk_update_manga(db, manga_data)     # 데이터베이스의 망가 데이터 업데이트
    print('update remaining_mangas:', len(remaining_mangas))
    inserted_manga = MangaCRUD.bulk_insert_manga(db, manga_data)     # 데이터베이스에 망가 데이터 삽입
    print('insert:', len(inserted_manga))
    if genre_name:
        genre_db = MangaCRUD.get_genre_by_name(db, genre_name)
        for manga in genre_db:
            if manga.folder_name not in [manga['folder_name'] for manga in manga_data]:
                MangaCRUD.delete_manga_models(db, manga)
                print(f'{manga.folder_name} deleted')       
    else:
        delete_count = MangaCRUD.bulk_delete_nonexistent_manga(db, manga_data) # 파일시스템에 존재하지 않는 망가 데이터 삭제
        print('bulk_delete:', delete_count)
    return {"detail": "Bulk update successful"}


@router.get("/mangas/", response_model=PaginatedMangaResponse)    # 페이지네이션된 망가 목록을 조회하는 API 엔드포인트
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
    # print('folders:', folders)
    # 허용된 정렬 필드 검증
    allowed_sort_fields = [
            "id", 
            "rating", 
            "create_date", 
            "update_date", 
            "file_date", 
            "page"
        ]
    # print('sort_by', sort_by)
    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by field. Allowed values are: {', '.join(allowed_sort_fields)}"
        )
    
    # 허용된 정렬 방향 검증
    if order not in ["asc", "desc", "random"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid order value. Must be either 'asc' or 'desc'"
        )
    
    skip = (page - 1) * size
    
    ###########################################
    # 500포인트 미만 이토준지만 볼수있음 
    if current_user.points < 500:       
        search = "이토준지"
        folders = ["__이토준지"]
    ###########################################
    
    mangas, total = MangaCRUD.get_mangas_with_pagination(
        db,
        user=current_user,
        skip=skip,
        limit=size,
        sort_by=sort_by,
        order=order,
        search=search,
        user_id=current_user.id if current_user else None,
        folders=folders     # genre
    )
    
    # total = MangaCRUD.get_total_manga_count(
    #     db, 
    #     search=search,
    #     folders=folders
    # )
    
    total_pages = ceil(total / size)
    
    ###################################################
    # 포인트 500미만 사용사 genre(folders) 이토준지만####
    if current_user.points < 500:
        genres = ['__이토준지']
    else:
        genres = get_genres_list()
    ###################################################    
    # print(mangas)
    print('total_pages:', total_pages)
    return PaginatedMangaResponse(
        items=mangas,
        total=total,
        page=page,
        size=size,
        pages=total_pages,
        genres=genres
    )
    

@router.post("/manga-actions/")
def manga_action(
        request: MangaActionRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
    """
    망가 목록에 대한 폴더 이동 병합 등의 액션을 처리합니다.
    """
    try:
        # 입력값 로깅
        # logger.info(f"Action request - action: {request.action}, manga_ids: {request.manga_ids}, target: {request.target_folder_name}")
        
        action = request.action
        manga_ids = request.manga_ids
        target_folder_name = request.target_folder_name

        # 망가 목록 조회
        mangas = []
        for manga_id in manga_ids:
            manga = MangaCRUD.get_manga_by_id(db, manga_id)
            if manga is None:
                # logger.error(f"Manga not found: id={manga_id}")
                raise HTTPException(
                    status_code=404,
                    detail=f"Manga not found: id={manga_id}"
                )
            mangas.append(manga)
        ################################################################################
        if action == 'move':
            try:
                # logger.info(f"Starting move operation for mangas: {manga_ids}")
                result = move_manga_folder(mangas, target_folder_name)
                # logger.debug(f"Move result: {result}")
                
                failures = [r for r in result if not r['success']]
                if failures:
                    error_messages = [f"{r['msg']}" for r in failures]
                    # logger.error(f"Move failures: {error_messages}")
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "message": "Some manga moves failed",
                            "errors": error_messages
                        }
                    )
                
                # 성공한 경우만 DB 업데이트
                successful_mangas = [r['manga'] for r in result if r['success']]
                # logger.info(f"Updating {len(successful_mangas)} manga records in DB")
                # print('successful_mangas:', successful_mangas)
                # for manga in successful_mangas:
                #     print('manga.id:', manga.id)
                #     print('manga.folder_name:', manga.folder_name)
                MangaCRUD.update_mangas_models(db, successful_mangas)
                # logger.info(f"Update successful")
                return result

            except ValueError as e:
                # logger.error(f"Value error during move: {str(e)}\n{traceback.format_exc()}")
                raise HTTPException(status_code=400, detail=str(e))
            except OSError as e:
                # logger.error(f"OS error during move: {str(e)}\n{traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"File system error: {str(e)}")
            except Exception as e:
                # logger.error(f"Unexpected error during move: {str(e)}\n{traceback.format_exc()}")
                raise

        elif action == 'merge':
            try:
                # logger.info(f"Starting merge operation for mangas: {manga_ids}")
                mangas.sort(key=lambda x: x.file_date, reverse=True)
                result = merge_manga_folder(mangas, target_folder_name)
                # logger.debug(f"Merge result: {result}")
                
                failures = [result['success']] if not result['success'] else []
                if failures:
                    error_messages = [f"{r['msg']}" for r in failures]
                    # logger.error(f"Merge failures: {error_messages}")
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "message": "Some manga merges failed",
                            "errors": error_messages
                        }
                    )

                # DB 업데이트
                t = 0
                while t<3:
                    try:
                        if result['success']:
                            for manga in mangas[1:]:
                                manga = db.merge(manga)
                                MangaCRUD.delete_manga_models(db, manga)
                                print(f"Deleting manga {manga.id}")
                            time.sleep(1)
                            mangas[0] = db.merge(mangas[0])
                            MangaCRUD.update_manga_models(db, mangas[0])
                            db.commit()
                            print(f"Updating manga {manga.id}")
                        return result
                    except Exception as e:
                        db.rollback()
                        print(f"Database error: {str(e)}")
                        print(traceback.format_exc())
                        raise HTTPException(status_code=500, detail=f"Database update failed: {str(e)}")
                        time.sleep(10)
                    t += 1
                    
                    
                    
                    
                    
                    
                    
                    # # 먼저 삭제될 manga들을 처리
                    # for r in result:
                    #     if r['success'] and '(삭제됨)' in r['msg']:
                    #         print(f"Deleting manga {r['manga'].id}")
                    #         MangaCRUD.delete_manga_models(db, r['manga'])
                    
                    # # commit으로 삭제 내용을 먼저 반영
                    # db.commit()
                    
                    # # 그 다음 유지될 manga 업데이트
                    # for r in result:
                    #     if r['success'] and '(유지됨)' in r['msg']:
                    #         manga = r['manga']
                    #         print(f"Updating manga {manga.id}")
                    #         MangaCRUD.update_manga_models(db, manga)
                            
                    # # 업데이트 내용 반영
                    # db.commit()
                    # return result
                
            
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except OSError as e:
                raise HTTPException(status_code=500, detail=f"File system error: {str(e)}")
            except Exception as e:
                raise

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action: {action}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    

@router.post("/{manga_id}/view")
def increment_manga_view(
        manga_id: int,
        db: Session = Depends(get_db)
    ):
    view_count = RatingCRUD.increment_view_count_manga(db, manga_id)
    if view_count is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"manga_id": manga_id, "view_count": view_count}










@router.get("/mangas/by-ids/", response_model=List[MangafolderName])
def get_mangas_by_ids(
        manga_ids: List[int] = Query(..., description="망가 ID 리스트"),
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user)
    ):
    """
    ID 리스트로 망가를 검색하는 엔드포인트
    
    Args:
        manga_ids: 검색할 망가 ID 리스트
        
    Returns:
        List[Manga]: 검색된 망가 리스트
    """
    try:
        mangas = []
        for manga_id in manga_ids:
            manga = MangaCRUD.get_manga_by_id(db, manga_id)
            if manga:
                mangas.append(manga)
        
        if not mangas:
            raise HTTPException(
                status_code=404,
                detail="No mangas found with provided IDs"
            )
            
        return mangas
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching mangas by IDs: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    


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

# @router.post("/{manga_id}/view")
# def record_view(
#         manga_id: int,
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user)
#     ):
#     """망가 조회 기록을 저장합니다."""
#     manga = MangaCRUD.get_manga_by_id(db, manga_id)
#     if not manga:
#         raise HTTPException(status_code=404, detail="Manga not found")
    
#     RatingCRUD.add_view_history(db, current_user.id, manga_id)
#     return {"message": "View recorded successfully"}

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



@router.post("/bulk-insert")
def bulk_insert_manga(
    base_folder_path: str=settings.IMAGE_DIRECTORY, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ):
    
    manga_data = list_images_from_folders(base_folder_path)            
    MangaCRUD.bulk_insert_manga(db, manga_data)   # insert
    return {"detail": "Bulk insert successful"}