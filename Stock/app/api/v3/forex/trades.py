from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from app.db.session import get_asset_db
from app.schemas import investment_schemas_v3 as schemas
from app.crud.v3 import forex as crud

router = APIRouter()

@router.post("/", response_model=schemas.Transaction)
async def create_forex_trade(
    trade: schemas.TradeRequest,
    db: Session = Depends(get_asset_db)
):
    """환전 거래 생성"""
    return await crud.create_forex_trade(db=db, trade=trade)

@router.get("/", response_model=List[Dict[str, Any]])
async def get_forex_trades(
    from_currency: Optional[str] = None,
    to_currency: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = None,
    broker: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_asset_db)
):
    """환전 거래 목록 조회"""
    return await crud.get_forex_trades(
        db=db,
        from_currency=from_currency,
        to_currency=to_currency,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        broker=broker,
        skip=skip,
        limit=limit
    )

@router.get("/summary", response_model=Dict[str, Any])
async def get_forex_trade_summary(
    start_date: date,
    end_date: date,
    currency_pair: Optional[str] = None,
    group_by: str = Query("daily", description="daily/monthly/currency"),
    db: Session = Depends(get_asset_db)
):
    """환전 거래 요약"""
    return await crud.get_forex_trade_summary(
        db=db,
        start_date=start_date,
        end_date=end_date,
        currency_pair=currency_pair,
        group_by=group_by
    )

@router.get("/pl", response_model=Dict[str, Any])
async def get_forex_pl(
    start_date: date,
    end_date: date,
    currency_pair: Optional[str] = None,
    include_unrealized: bool = False,
    db: Session = Depends(get_asset_db)
):
    """환전 손익 계산"""
    return await crud.get_forex_pl(
        db=db,
        start_date=start_date,
        end_date=end_date,
        currency_pair=currency_pair,
        include_unrealized=include_unrealized
    )

@router.get("/positions", response_model=List[Dict[str, Any]])
async def get_forex_positions(
    currency: Optional[str] = None,
    include_closed: bool = False,
    db: Session = Depends(get_asset_db)
):
    """통화별 포지션 조회"""
    return await crud.get_forex_positions(
        db=db,
        currency=currency,
        include_closed=include_closed
    )

@router.post("/convert", response_model=Dict[str, float])
async def convert_currency(
    amount: float = Query(..., gt=0),
    from_currency: str = Query(...),
    to_currency: str = Query(...),
    date: Optional[date] = None,
    db: Session = Depends(get_asset_db)
):
    """통화 환산"""
    return await crud.convert_currency(
        db=db,
        amount=amount,
        from_currency=from_currency,
        to_currency=to_currency,
        date=date
    )