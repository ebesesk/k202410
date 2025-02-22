from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_asset_db
from app.schemas import investment_schemas_v3 as schemas
from app.crud.v3 import trades_transactions as crud

router = APIRouter()

@router.post("")
def create_trade():
    return {"result": "success"}


# @router.post("/", response_model=schemas.AssetTransaction)
# async def create_trade(
#     trade_request: schemas.TradeRequest,
#     db: Session = Depends(get_asset_db)
# ):
#     """자산 매매 거래 생성"""
#     return await crud.create_trade(db=db, trade_request=trade_request)

# @router.get("/", response_model=List[schemas.AssetTransaction])
# async def get_trades(
#     asset_id: Optional[int] = None,
#     trade_type: Optional[str] = None,
#     start_date: Optional[datetime] = None,
#     end_date: Optional[datetime] = None,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=1000),
#     db: Session = Depends(get_asset_db)
# ):
#     """자산 매매 거래 목록 조회"""
#     return await crud.get_trades(
#         db=db,
#         asset_id=asset_id,
#         trade_type=trade_type,
#         start_date=start_date,
#         end_date=end_date,
#         skip=skip,
#         limit=limit
#     )