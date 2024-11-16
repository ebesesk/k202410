from sqlalchemy.orm import Session
from app.models.rating import UserMangaRating
from typing import List, Dict
from sqlalchemy import func
from app.models.manga import Manga
from app.models.video import Video
from app.models.rating import VideoRating
from app.crud.manga import MangaCRUD
from app.crud import video as VideoCRUD

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

    @staticmethod   # manga rating
    def add_or_update_rating(db: Session, user_id: int, manga_id: int, rating: float) -> UserMangaRating:
        """평점을 추가하거나 업데이트합니다."""
        existing_rating = db.query(UserMangaRating).filter(
            UserMangaRating.user_id == user_id,
            UserMangaRating.manga_id == manga_id
        ).first()

        if existing_rating:
            # 기존 평점이 있는 경우, 평점 수정
            old_rating = existing_rating.rating
            existing_rating.rating = rating
            
            # 비디오의 전체 평점 업데이트 (이전 평점 제거 후 새 평점 추가)
            manga = db.query(Manga).filter(Manga.id == manga_id).first()
            
            if manga:
                if not manga.rating_sum:
                    manga.rating_sum = 0
                if not manga.rating_average:
                    manga.rating_average = 0
                manga.rating_sum = manga.rating_sum - old_rating + rating
                manga.rating_average = manga.rating_sum / manga.rating_count
        else:
            existing_rating = UserMangaRating(
                user_id=user_id,
                manga_id=manga_id,
                rating=rating
            )
            db.add(existing_rating)
            
            # manga의 전체 평점 업데이트
            manga = db.query(Manga).filter(Manga.id == manga_id).first()
            if manga:
                if not manga.rating_sum:
                    manga.rating_sum = 0
                if not manga.rating_average:
                    manga.rating_average = 0
                if not manga.rating_count:
                    manga.rating_count = 0
                manga.rating_sum += rating
                manga.rating_count += 1
                manga.rating_average = manga.rating_sum / manga.rating_count
        db.commit()
        db.refresh(existing_rating)
        return existing_rating
    
    @staticmethod
    def increment_view_count_manga(db: Session, manga_id:int):
        manga = db.query(Manga).filter(Manga.id == manga_id).first()
        if manga:
            if not manga.view_count:
                manga.view_count = 0
            manga.view_count += 1
            db.commit()
            return manga.view_count
        return None
    
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
    
    @staticmethod
    def add_or_update_video_rating(db: Session, user_id: int, video_id: int, rating: int):
        # 기존 평점이 있는지 확인
        video_rating = db.query(VideoRating).filter(
            VideoRating.user_id == user_id, 
            VideoRating.video_id == video_id
        ).first()
        
        if video_rating:
            # 기존 평점이 있는 경우, 평점 수정
            old_rating = video_rating.rating
            video_rating.rating = rating
            
            # 비디오의 전체 평점 업데이트 (이전 평점 제거 후 새 평점 추가)
            video = db.query(Video).filter(Video.id == video_id).first()
            
            if video:
                if not video.rating_sum:
                    video.rating_sum = 0
                if not video.rating_average:
                    video.rating_average = 0
                video.rating_sum = video.rating_sum - old_rating + rating
                video.rating_average = video.rating_sum / video.rating_count
            # else:
            #     video.rating_sum = rating
            #     video.rating_count = 1
            #     video.rating_average = video.rating_sum / video.rating_count
        else:
            # 새로운 평점 추가
            video_rating = VideoRating(
                user_id=user_id,
                video_id=video_id,
                rating=rating
            )
            db.add(video_rating)
            
            # 비디오의 전체 평점 업데이트
            video = db.query(Video).filter(Video.id == video_id).first()
            if video:
                if not video.rating_sum:
                    video.rating_sum = 0
                if not video.rating_average:
                    video.rating_average = 0
                if not video.rating_count:
                    video.rating_count = 0
                video.rating_sum += rating
                video.rating_count += 1
                video.rating_average = video.rating_sum / video.rating_count
        
        db.commit()
        db.refresh(video_rating)
        return video_rating
        
    @staticmethod
    def increment_view_count_video(db: Session, video_id: int):
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            if not video.view_count:
                video.view_count = 0
            video.view_count += 1
            db.commit()
            return video.view_count
        return None
    
    # app/crud/rating.py
    @staticmethod    
    def get_video_rating(db: Session, user_id: int, video_id: int):
        # print(user_id, video_id)
        return db.query(VideoRating).filter(VideoRating.user_id == user_id, VideoRating.video_id == video_id).first()
    
    
    @staticmethod
    def update_video_rating(video_id, new_rating, db: Session):
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.rating_sum += new_rating
            video.rating_count += 1
            video.rating_average = video.rating_sum / video.rating_count
            db.commit()