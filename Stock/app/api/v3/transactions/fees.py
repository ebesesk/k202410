from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_asset_db
from app.schemas import investment_schemas_v3 as schemas
from app.crud.v3 import fee_transactions as crud

router = APIRouter()

@router.post("/", response_model=schemas.FeeTransaction)
async def create_fee(
    fee: schemas.FeeTransactionCreate,
    db: Session = Depends(get_asset_db)
):
    """수수료 거래 생성"""
    return await crud.create_fee_transaction(db=db, fee=fee)

@router.get("/", response_model=List[schemas.FeeTransaction])
async def get_fee_transactions(
    fee_type: Optional[str] = None,
    reference_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_asset_db)
):
    """수수료 거래 목록 조회"""
    return await crud.get_fee_transactions(
        db=db,
        fee_type=fee_type,
        reference_id=reference_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )