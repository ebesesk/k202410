from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date
from app.db.session import get_asset_db
from app.schemas import investment_schemas_v3 as schemas
from app.crud.v3 import assets as crud

router = APIRouter()

@router.get("/")
def get_asset_prices():
    """자산 가격 목록 조회"""
    return {"result": "success"}

# @router.post("/", response_model=schemas.AssetPrice)
# async def create_asset_price(
#     price: schemas.AssetPriceCreate,
#     db: Session = Depends(get_asset_db)
# ):
#     """자산 가격 등록"""
#     return await crud.create_asset_price(db=db, price=price)

# @router.get("/historical", response_model=List[Dict[str, Any]])
# async def get_historical_prices(
#     asset_id: int,
#     start_date: date,
#     end_date: date,
#     interval: str = Query("daily", description="daily/weekly/monthly"),
#     db: Session = Depends(get_asset_db)
# ):
#     """과거 가격 이력 조회"""
#     return await crud.get_historical_prices(
#         db=db,
#         asset_id=asset_id,
#         start_date=start_date,
#         end_date=end_date,
#         interval=interval
#     )

# @router.get("/latest", response_model=Dict[str, float])
# async def get_latest_prices(
#     asset_ids: List[int] = Query(...),
#     db: Session = Depends(get_asset_db)
# ):
#     """최신 가격 조회"""
#     return await crud.get_latest_prices(db=db, asset_ids=asset_ids)