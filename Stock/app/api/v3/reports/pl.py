from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date
from app.db.session import get_asset_db
from app.crud.v3 import forex as crud

router = APIRouter()

# @router.get("/daily", response_model=List[Dict[str, Any]])
# async def get_daily_pl(
#     start_date: date,
#     end_date: date,
#     asset_id: Optional[int] = None,
#     asset_type: Optional[str] = None,
#     db: Session = Depends(get_asset_db)
# ):
#     """일별 손익 보고서"""
#     return await crud.get_daily_pl(
#         db=db,
#         start_date=start_date,
#         end_date=end_date,
#         asset_id=asset_id,
#         asset_type=asset_type
#     )

# @router.get("/monthly", response_model=List[Dict[str, Any]])
# async def get_monthly_pl(
#     year: int = Query(..., ge=2000, le=2100),
#     month: Optional[int] = Query(None, ge=1, le=12),
#     asset_type: Optional[str] = None,
#     db: Session = Depends(get_asset_db)
# ):
#     """월별 손익 보고서"""
#     return await crud.get_monthly_pl(
#         db=db,
#         year=year,
#         month=month,
#         asset_type=asset_type
#     )

# @router.get("/realized", response_model=List[Dict[str, Any]])
# async def get_realized_pl(
#     start_date: Optional[date] = None,
#     end_date: Optional[date] = None,
#     asset_id: Optional[int] = None,
#     asset_type: Optional[str] = None,
#     db: Session = Depends(get_asset_db)
# ):
#     """실현 손익 보고서"""
#     return await crud.get_realized_pl(
#         db=db,
#         start_date=start_date,
#         end_date=end_date,
#         asset_id=asset_id,
#         asset_type=asset_type
#     )

# @router.get("/unrealized", response_model=List[Dict[str, Any]])
# async def get_unrealized_pl(
#     asset_id: Optional[int] = None,
#     asset_type: Optional[str] = None,
#     db: Session = Depends(get_asset_db)
# ):
#     """미실현 손익 보고서"""
#     return await crud.get_unrealized_pl(
#         db=db,
#         asset_id=asset_id,
#         asset_type=asset_type
#     )