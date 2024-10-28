from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from app.models.manga import Manga
# from app.schemas.manga import MangaCreat
from typing import List, Dict, Optional, Any
from datetime import datetime

class MangaCRUD:
    """
    망가 CRUD 작업을 위한 정적 메서드들을 포함하는 클래스
    모든 데이터베이스 조작 로직을 캡슐화합니다.
    """
    @staticmethod
    def bulk_insert_manga(db: Session, mangas: List[Dict]):
        # 이미 DB에 있는 레코드의 folder_name 가져오기
        existing_folder_names = {manga.folder_name for manga in db.query(Manga.folder_name).all()}

        # 새로운 레코드만 삽입
        new_mangas = []
        for manga_data in mangas:
            # 필요한 데이터 처리 및 유효성 검사
            folder_name = manga_data.get("folder_name")
            page_count = manga_data.get("page")
            images_name = manga_data.get("images_name")
            create_date = manga_data.get("create_date")
            update_date = manga_data.get("update_date")
            file_date = manga_data.get("file_date")

            # 폴더 이름이 기존에 없고, 모든 필요한 데이터가 제공되었는지 확인
            if folder_name and folder_name not in existing_folder_names and isinstance(page_count, int):
                # datetime 변환이 필요할 경우
                if isinstance(create_date, str):
                    create_date = datetime.fromisoformat(create_date)
                if isinstance(update_date, str):
                    update_date = datetime.fromisoformat(update_date)
                if isinstance(file_date, str):
                    file_date = datetime.fromisoformat(file_date)

                new_manga = Manga(
                    folder_name=folder_name,
                    page=int(page_count),
                    images_name=images_name,
                    create_date=create_date,
                    update_date=update_date,
                    file_date=file_date
                )
                new_mangas.append(new_manga)

        if new_mangas:
            db.bulk_save_objects(new_mangas)
            db.commit()
            
    @staticmethod
    def get_mangas_with_pagination(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "id",
        order: str = "desc",
        search: Optional[str] = None
    ) -> List[Manga]:
        """
        페이지네이션과 정렬, 검색이 적용된 망가 목록을 조회합니다.
        
        Args:
            db (Session): 데이터베이스 세션
            skip (int): 건너뛸 레코드 수
            limit (int): 반환할 최대 레코드 수
            sort_by (str): 정렬 기준 필드
            order (str): 정렬 방향 ('asc' 또는 'desc')
            search (Optional[str]): 검색어 (폴더명이나 태그에서 검색)
        
        Returns:
            List[Manga]: 페이지네이션된 망가 목록
        """
        query = db.query(Manga)
        
        if search:
            query = query.filter(
                or_(
                    Manga.folder_name.ilike(f"%{search}%"),
                    Manga.tags.ilike(f"%{search}%")
                )
            )
        
        if order.lower() == "desc":
            query = query.order_by(desc(getattr(Manga, sort_by)))
        else:
            query = query.order_by(getattr(Manga, sort_by))
        
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_total_manga_count(db: Session, search: Optional[str] = None) -> int:
        """
        전체 망가 수를 조회합니다.
        
        Args:
            db (Session): 데이터베이스 세션
            search (Optional[str]): 검색어
        
        Returns:
            int: 전체 망가 수
        """
        query = db.query(Manga)
        if search:
            query = query.filter(
                or_(
                    Manga.folder_name.ilike(f"%{search}%"),
                    Manga.tags.ilike(f"%{search}%")
                )
            )
        return query.count()

    @staticmethod
    def get_manga_by_id(db: Session, manga_id: int) -> Optional[Manga]:
        """
        ID로 특정 망가를 조회합니다.
        
        Args:
            db (Session): 데이터베이스 세션
            manga_id (int): 망가 ID
            
        Returns:
            Optional[Manga]: 찾은 망가 객체 또는 None
        """
        return db.query(Manga).filter(Manga.id == manga_id).first()

    @staticmethod
    def get_manga_by_folder_name(db: Session, folder_name: str) -> Optional[Manga]:
        """
        폴더명으로 특정 망가를 조회합니다.
        
        Args:
            db (Session): 데이터베이스 세션
            folder_name (str): 망가 폴더명
            
        Returns:
            Optional[Manga]: 찾은 망가 객체 또는 None
        """
        return db.query(Manga).filter(Manga.folder_name == folder_name).first()

    @staticmethod
    def create_manga(db: Session, manga_data: Dict[str, Any]) -> Manga:
        """
        새로운 망가를 생성합니다.
        
        Args:
            db (Session): 데이터베이스 세션
            manga_data (Dict[str, Any]): 생성할 망가 데이터
            
        Returns:
            Manga: 생성된 망가 객체
        """
        manga = Manga(**manga_data)
        db.add(manga)
        db.commit()
        db.refresh(manga)
        return manga

    @staticmethod
    def update_manga(
        db: Session,
        manga_id: int,
        manga_data: Dict[str, Any]
    ) -> Optional[Manga]:
        """
        기존 망가 정보를 업데이트합니다.
        
        Args:
            db (Session): 데이터베이스 세션
            manga_id (int): 업데이트할 망가 ID
            manga_data (Dict[str, Any]): 업데이트할 데이터
            
        Returns:
            Optional[Manga]: 업데이트된 망가 객체 또는 None
        """
        manga = MangaCRUD.get_manga_by_id(db, manga_id)
        if manga:
            manga_data["update_date"] = datetime.utcnow()
            for key, value in manga_data.items():
                setattr(manga, key, value)
            db.commit()
            db.refresh(manga)
        return manga

    @staticmethod
    def delete_manga(db: Session, manga_id: int) -> bool:
        """
        망가를 삭제합니다.
        
        Args:
            db (Session): 데이터베이스 세션
            manga_id (int): 삭제할 망가 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        manga = MangaCRUD.get_manga_by_id(db, manga_id)
        if manga:
            db.delete(manga)
            db.commit()
            return True
        return False

    @staticmethod
    def search_mangas(
        db: Session,
        search_term: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[Manga]:
        """
        망가를 검색합니다.
        
        Args:
            db (Session): 데이터베이스 세션
            search_term (str): 검색어
            skip (int): 건너뛸 레코드 수
            limit (int): 반환할 최대 레코드 수
            
        Returns:
            List[Manga]: 검색된 망가 목록
        """
        return db.query(Manga).filter(
            or_(
                Manga.folder_name.ilike(f"%{search_term}%"),
                Manga.tags.ilike(f"%{search_term}%")
            )
        ).offset(skip).limit(limit).all()

    # app/api/api_v1/endpoints/manga.py에서 사용 예시:
    # @router.get("/mangas/", response_model=PaginatedMangaResponse)
    # def read_mangas(
    #     db: Session = Depends(get_db),
    #     page: int = Query(1, ge=1, description="페이지 번호"),
    #     size: int = Query(10, ge=1, le=100, description="페이지당 아이템 수"),
    #     sort_by: str = Query("id", description="정렬 기준 필드"),
    #     order: str = Query("desc", description="정렬 방향 (asc/desc)"),
    #     search: Optional[str] = Query(None, description="검색어")
    # ):
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