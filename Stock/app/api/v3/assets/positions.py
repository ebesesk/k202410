from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date
from app.db.session import get_asset_db
from app.schemas import investment_schemas_v3 as schemas
from app.crud.v3 import assets as crud

router = APIRouter()

@router.get("")
def get_positions():
    return {"result": "success"}


# @router.get("/", response_model=List[schemas.Position])
# async def get_positions(
#     asset_type: Optional[str] = None,
#     currency: Optional[str] = None,
#     include_closed: bool = False,
#     db: Session = Depends(get_asset_db)
# ):
#     """포지션 목록 조회"""
#     return await crud.get_positions(
#         db=db,
#         asset_type=asset_type,
#         currency=currency,
#         include_closed=include_closed
#     )

# @router.get("/summary", response_model=Dict[str, Any])
# async def get_position_summary(
#     group_by: str = Query("asset_type", description="asset_type/currency/broker"),
#     currency: str = "KRW",
#     db: Session = Depends(get_asset_db)
# ):
#     """포지션 요약"""
#     return await crud.get_position_summary(
#         db=db,
#         group_by=group_by,
#         currency=currency
#     )

# @router.get("/{asset_id}", response_model=schemas.Position)
# async def get_asset_position(
#     asset_id: int,
#     include_history: bool = False,
#     db: Session = Depends(get_asset_db)
# ):
#     """특정 자산의 포지션 조회"""
#     return await crud.get_asset_position(
#         db=db,
#         asset_id=asset_id,
#         include_history=include_history
#     )