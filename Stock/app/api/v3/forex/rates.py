from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from app.db.session import get_asset_db
from app.schemas import investment_schemas_v3 as schemas
from app.crud.v3 import forex as crud

router = APIRouter()

# @router.get("/current", response_model=Dict[str, float])
# async def get_current_rates(
#     base_currency: str = "KRW",
#     target_currencies: Optional[List[str]] = Query(None),
#     db: Session = Depends(get_asset_db)
# ):
#     """현재 환율 조회"""
#     return await crud.get_current_rates(
#         db=db,
#         base_currency=base_currency,
#         target_currencies=target_currencies
#     )

# @router.get("/historical", response_model=List[Dict[str, Any]])
# async def get_historical_rates(
#     from_currency: str,
#     to_currency: str,
#     start_date: date,
#     end_date: date,
#     interval: str = Query("daily", description="daily/weekly/monthly"),
#     db: Session = Depends(get_asset_db)
# ):
#     """과거 환율 이력 조회"""
#     return await crud.get_historical_rates(
#         db=db,
#         from_currency=from_currency,
#         to_currency=to_currency,
#         start_date=start_date,
#         end_date=end_date,
#         interval=interval
#     )

# @router.post("/rates", response_model=schemas.ExchangeRate)
# async def create_exchange_rate(
#     rate: schemas.ExchangeRate,
#     db: Session = Depends(get_asset_db)
# ):
#     """환율 정보 등록"""
#     return await crud.create_exchange_rate(db=db, rate=rate)

# @router.get("/rates/{date}", response_model=Dict[str, Dict[str, float]])
# async def get_rates_by_date(
#     date: date,
#     currencies: Optional[List[str]] = Query(None),
#     db: Session = Depends(get_asset_db)
# ):
#     """특정 날짜의 환율 정보 조회"""
#     return await crud.get_rates_by_date(
#         db=db,
#         date=date,
#         currencies=currencies
#     )

# @router.get("/stats", response_model=Dict[str, Any])
# async def get_exchange_rate_stats(
#     from_currency: str,
#     to_currency: str,
#     start_date: date,
#     end_date: date,
#     db: Session = Depends(get_asset_db)
# ):
#     """환율 통계 정보"""
#     return await crud.get_exchange_rate_stats(
#         db=db,
#         from_currency=from_currency,
#         to_currency=to_currency,
#         start_date=start_date,
#         end_date=end_date
#     )