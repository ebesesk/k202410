from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import func, and_
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.models.investment_models import Transaction, Position, Portfolio
from app.schemas import investment_schemas_v2 as schemas
from app.utils.utils import get_current_kst_time

# get Position
def get_positions(db: Session, username: str, page: int = 1, limit: int = 10):
    # 전체 아이템 수 계산
    total_items = db.query(func.count(Position.id)).filter(
        Position.username == username
    ).scalar()
    
    # 페이지네이션 적용 (asset 관계 포함)
    positions = db.query(Position).options(
        joinedload(Position.asset)  # asset 관계 로드
    ).filter(
        Position.username == username
    ).offset((page - 1) * limit).limit(limit).all()
    
    return {
        "items": positions,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_items": total_items,
            "total_pages": (total_items + limit - 1) // limit
        }
    }

# def get_position_by_symbol(db: Session, symbol: str, username: str):
#     return db.query(Position).filter(Position.symbol == symbol, Position.username == username).first()

def get_position_by_asset_id(db: Session, asset_id: int, username: str):
    return db.query(Position).filter(Position.asset_id == asset_id, Position.username == username).first()

def get_position_by_id(db: Session, position_id: int, username: str):
    return db.query(Position).filter(Position.id == position_id, Position.username == username).first()