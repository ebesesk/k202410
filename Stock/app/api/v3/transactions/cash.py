from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_asset_db
from app.schemas import investment_schemas_v3 as schemas
from app.crud.v3 import cash_transactions as crud

router = APIRouter()

@router.post("/", response_model=schemas.CashTransaction)
async def create_cash_transaction(
    cash_tx: schemas.CashTransactionCreate,
    db: Session = Depends(get_asset_db)
):
    """현금 거래 생성"""
    return await crud.create_cash_transaction(db=db, cash_tx=cash_tx)

@router.get("/", response_model=List[schemas.CashTransaction])
async def get_cash_transactions(
    cash_type: Optional[str] = None,
    account_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_asset_db)
):
    """현금 거래 목록 조회"""
    return await crud.get_cash_transactions(
        db=db,
        cash_type=cash_type,
        account_id=account_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )