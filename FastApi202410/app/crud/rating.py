from sqlalchemy.orm import Session
from app.models.rating import UserMangaRating
from typing import List, Dict
from sqlalchemy import func
from app.models.manga import Manga

class RatingCRUD:
    @staticmethod
    def get_user_ratings(db: Session, user_id: int) -> List[Dict]:
        """사용자의 모든 평점을 조회합니다."""
        ratings = db.query(UserMangaRating).filter(
            UserMangaRating.user_id == user_id
        ).all()
        
        return [
            {"manga_id": rating.manga_id, "rating": rating.rating} 
            for rating in ratings
        ]

    @staticmethod
    def add_or_update_rating(db: Session, user_id: int, manga_id: int, rating: float) -> UserMangaRating:
        """평점을 추가하거나 업데이트합니다."""
        existing_rating = db.query(UserMangaRating).filter(
            UserMangaRating.user_id == user_id,
            UserMangaRating.manga_id == manga_id
        ).first()

        if existing_rating:
            existing_rating.rating = rating
        else:
            existing_rating = UserMangaRating(
                user_id=user_id,
                manga_id=manga_id,
                rating=rating
            )
            db.add(existing_rating)
        
        db.commit()
        db.refresh(existing_rating)
        return existing_rating

    @staticmethod
    def delete_rating(db: Session, user_id: int, manga_id: int) -> bool:
        """평점을 삭제합니다."""
        rating = db.query(UserMangaRating).filter(
            UserMangaRating.user_id == user_id,
            UserMangaRating.manga_id == manga_id
        ).first()
        
        if rating:
            db.delete(rating)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_recommended_mangas(db: Session, user_id: int, limit: int = 10) -> List[Manga]:
        """사용자의 평점을 기반으로 추천 망가를 반환합니다."""
        # 사용자가 높은 평점을 준 망가들의 특성을 기반으로 추천
        # 여기서는 간단히 평균 평점이 높은 망가들을 추천
        return db.query(Manga)\
            .join(UserMangaRating)\
            .group_by(Manga.id)\
            .having(func.avg(UserMangaRating.rating) >= 4.0)\
            .order_by(func.avg(UserMangaRating.rating).desc())\
            .limit(limit)\
            .all()