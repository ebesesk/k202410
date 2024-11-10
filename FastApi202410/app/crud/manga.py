from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_
from app.models.manga import Manga
# from app.schemas.manga import MangaCreat
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
from zoneinfo import ZoneInfo  # 새로운 import 추가
from sqlalchemy import func, asc, desc
from app.schemas.manga import MangaResponse
from app.models.rating import UserMangaRating
import time

KST = ZoneInfo("Asia/Seoul")  # KST 정의

class MangaCRUD:
    """
    망가 CRUD 작업을 위한 정적 메서드들을 포함하는 클래스
    모든 데이터베이스 조작 로직을 캡슐화합니다.
    """
    
    @staticmethod
    def get_manga_by_id(db: Session, manga_id: int) -> Manga:
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
    def get_genre_by_name(db: Session, genre_name: str) -> Optional[Manga]:
        return db.query(Manga).filter(Manga.folder_name.like(f"{genre_name}/%")).all()
    
    @staticmethod
    def bulk_update_manga(db: Session, mangas: List[Dict]):
        '''
        manga 데이터 folder_name 이 존재하는 경우 update_date 를 현재 시간으로,
        images_name 을 일괄 업데이트 합니다.
        '''
        # 먼저 DB에 데이터가 있는지 확인
        manga_count = db.query(Manga).count()
        if manga_count == 0:
            print("DB에 업데이트할 데이터가 없습니다.")
            return mangas
        
        manga_updates = []
        remaining_mangas = []
        
        for manga_data in mangas:
            manga_db = MangaCRUD.get_manga_by_folder_name(db, manga_data["folder_name"])
            # print(manga_db)
            # if manga_db and manga_data["page"] != manga_db.page:
            if manga_db and manga_data["tags"] != manga_db.tags:
                # print(f"업데이트할 manga 찾음: {manga_data['folder_name']}")
                tags_db = json.loads(manga_db.tags)
                tags_db['size'] = manga_data["tags"]["size"]
                manga_updates.append({
                    "id": manga_db.id,
                    "page": len(manga_data["images_name"]),
                    "tags": json.dumps(tags_db),
                    "images_name": json.dumps(manga_data["images_name"]),
                    "update_date": datetime.now(KST),
                    "file_date": manga_data["file_date"]
                })
            else:
                remaining_mangas.append(manga_data)
        
        if manga_updates:
            try:
                db.bulk_update_mappings(Manga, manga_updates)
                db.commit()
                print(f"총 {len(manga_updates)}개의 레코드가 업데이트되었습니다.")
            except Exception as e:
                print(f"업데이트 중 오류 발생: {str(e)}")
                db.rollback()
                raise
        else:
            print("업데이트할 데이터가 없습니다.")
        
        return remaining_mangas
    
    @staticmethod
    def bulk_delete_nonexistent_manga(db: Session, existing_manga_data: List[Dict]) -> int:
        """
        파일시스템에 존재하지 않는 망가 데이터를 데이터베이스에서 삭제합니다.
        """
        # 파일시스템의 모든 폴더명 가져오기 (list_images_from_folders의 결과에서)
        all_folder_names = [manga["folder_name"] for manga in existing_manga_data]

        # DB에서 파일시스템에 없는 레코드 찾기
        to_delete = db.query(Manga).filter(
            ~Manga.folder_name.in_(all_folder_names)
        ).all()
        
        delete_count = len(to_delete)
        
        # 레코드 삭제
        for manga in to_delete:
            db.delete(manga)
        
        db.commit()

        return delete_count
    
    
    
    @staticmethod
    def bulk_insert_manga(db: Session, mangas: List[Dict]):
        '''
        파일 리스트에서 새로운 망가 데이터를 삽입합니다.
        '''
        # 이미 DB에 있는 레코드의 folder_name 가져오기
        existing_folder_names = {manga.folder_name for manga in db.query(Manga.folder_name).all()}
        # 새로운 레코드만 삽입
        new_mangas = []
        for i, manga_data in enumerate(mangas):
            # 필요한 데이터 처리 및 유효성 검사
            folder_name = manga_data.get("folder_name")
            page_count = manga_data.get("page")
            images_name = manga_data.get("images_name")
            # create_date = manga_data.get("create_date")
            # update_date = manga_data.get("update_date")
            file_date = manga_data.get("file_date")
            tags = manga_data.get("tags")

            # 폴더 이름이 기존에 없고, 모든 필요한 데이터가 제공되었는지 확인
            if folder_name and folder_name not in existing_folder_names and len(images_name) > 0:
                # datetime 변환이 필요할 경우
                # if isinstance(create_date, str):
                #     create_date = datetime.fromisoformat(create_date)
                # if isinstance(update_date, str):
                #     update_date = datetime.fromisoformat(update_date)
                # if isinstance(file_date, str):
                #     file_date = datetime.fromisoformat(file_date)

                new_manga = Manga(
                    folder_name=folder_name,
                    page=int(page_count),
                    tags=json.dumps(tags),
                    images_name=json.dumps(images_name),
                    create_date=datetime.now(KST),
                    update_date=datetime.now(KST),
                    file_date=file_date
                )
                new_mangas.append(new_manga)
                # mangas.pop(i)
        if new_mangas:
            db.bulk_save_objects(new_mangas)
            db.commit()

        return new_mangas
            
    @staticmethod
    def get_mangas_with_pagination(
            db: Session,
            skip: int = 0,
            limit: int = 10,
            sort_by: str = "id",
            order: str = "desc",
            search: Optional[str] = None,
            user_id: Optional[int] = None,
            folders: Optional[List[str]] = None
        ) -> List[Manga]:
        # 평균 평점 계산을 위해 외부 조인 적용
        query = db.query(
                Manga,
                func.avg(UserMangaRating.rating).label('avg_rating')
            ).outerjoin(UserMangaRating)
        
        # 검색 조건과 폴더 조건을 하나의 or_ 조건으로 통합
        conditions = []

        # 검색어 조건 추가
        if search:
            search = search.replace(" ", "_")
            search_term = f"%{search}%"
            
            tags_filter = []
            for item in query.all():
                tag_titles = ''
                tags = json.loads(item[0].tags)
                try:
                    for tag in tags['titles']:
                        tag_titles += tag + '_'
                    if search_term in tag_titles:
                        tags_filter.append(item[0])
                except:
                    pass
            conditions.append(Manga.folder_name.ilike(search_term) | or_(*tags_filter))

        # print(folders)
        # 폴더 조건 추가
        if folders:
            querys = [Manga.folder_name.ilike(f"{folder}/%") for folder in folders if isinstance(folder, str)]
            conditions.append(or_(*querys))

        # 조건이 있는 경우에만 필터 적용
        if conditions:
            query = query.filter(and_(*conditions))
            
        # Group by 추가
        query = query.group_by(Manga.id)
                    
        # 정렬 적용
        if sort_by == "file_date":
            if order == "asc":
                query = query.order_by(asc(Manga.file_date))
            elif order == "desc":
                query = query.order_by(desc(Manga.file_date))
            else:
                query = query.order_by(func.random())
                
        elif sort_by == "rating":
            # 평점 기준 정렬
            if order == "asc": 
                query = query.order_by(asc('avg_rating'), asc(Manga.id))
            elif order == "desc":
                query = query.order_by(desc('avg_rating'), desc(Manga.id))
            else:
                query = query.order_by(func.random())
        else:
            # 다른 필드 기준 정렬
            if order == "asc":
                query = query.order_by(asc(getattr(Manga, sort_by)))
            elif order == "desc":
                query = query.order_by(desc(getattr(Manga, sort_by)))
            else:
                query = query.order_by(func.random())
        
        # 페이지네이션 적용 및 결과 추출
        results = query.offset(skip).limit(limit).all()
    
        # 결과에서 Manga 객체만 추출
        mangas = [result[0] for result in results]
        
        if user_id:
            for manga in mangas:
                # 사용자 평점 조회
                rating = db.query(UserMangaRating).filter(
                    UserMangaRating.manga_id == manga.id,
                    UserMangaRating.user_id == user_id
                ).first()
                manga.user_rating = rating.rating if rating else None
                
                # 평균 평점 설정
                avg_rating = next((r[1] for r in results if r[0].id == manga.id), None)
                manga.rating_average = float(avg_rating) if avg_rating else 0.0
            
        return mangas

    


    @staticmethod
    def get_total_manga_count(
            db: Session,
            search: Optional[str] = None,
            folders: Optional[List[str]] = None
        ) -> int:
        """
        전체 망가 수를 조회합니다.
        
        Args:
            db (Session): 데이터베이스 세션
            search (Optional[str]): 검색어
        
        Returns:
            int: 전체 망가 수
        """
        query = db.query(Manga)
        # 검색 조건과 폴더 조건을 하나의 리스트로 통합
        conditions = []
        
        if search:
            search = search.replace(" ", "_")
            search_term = f"%{search}%"
            conditions.append(Manga.folder_name.ilike(search_term) | Manga.tags.ilike(search_term))
        
        if folders:
            querys = [Manga.folder_name.ilike(f"%{folder}/%") for folder in folders if isinstance(folder, str)]
            conditions.append(or_(*querys))
        
        # 조건이 있는 경우에만 필터 적용
        if conditions:
            query = query.filter(and_(*conditions))
        
        return query.count()

    

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
    def update_mangas(
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
            manga_data["update_date"] = datetime.now(KST)
            for key, value in manga_data.items():
                setattr(manga, key, value)
            db.commit()
            db.refresh(manga)
        return manga

    @staticmethod
    def update_manga_models(db: Session, manga: Manga) -> Manga:
        manga.update_date = datetime.now(KST)
        db.commit()
        db.refresh(manga)
        return manga
    
    @staticmethod
    def update_mangas_models(db: Session, mangas: List[Manga]) -> List[Manga]:
        for manga in mangas:
            db.commit()
            db.refresh(manga)
        return mangas

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
    def delete_mangas_models(db: Session, mangas: List[Manga]) -> bool:
        for manga in mangas:
            db.delete(manga)
        db.commit()
        return True

    @staticmethod
    def delete_manga_models(db: Session, manga: Manga) -> bool:
        db.delete(manga)
        db.commit()
        # db.refresh(manga)
        # time.sleep(3)
        return True

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

    
    
