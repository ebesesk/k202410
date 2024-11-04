from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class RatingBase(BaseModel):
    manga_id: int
    rating: float = Field(..., ge=1, le=5)

class RatingCreate(BaseModel):
    rating: float = Field(..., ge=0, le=5, description="평점 (0-5)")

class Rating(RatingBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class HistoryBase(BaseModel):
    manga_id: int

class HistoryCreate(HistoryBase):
    pass

class History(HistoryBase):
    id: int
    user_id: int
    view_count: int
    last_viewed: datetime

    class Config:
        from_attributes = True

class MangaRecommendation(BaseModel):
    id: int
    folder_name: str
    tags: Optional[str]
    rating_average: float
    view_count: int
    recommendation_score: float

    class Config:
        from_attributes = True

class RecommendationResponse(BaseModel):
    recommendations: List[MangaRecommendation]
    total: int