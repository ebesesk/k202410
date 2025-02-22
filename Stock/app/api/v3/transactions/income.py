from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_asset_db
from app.schemas import investment_schemas_v3 as schemas
from app.crud.v3 import income_transactions as crud

router = APIRouter()

@router.post("/", response_model=schemas.IncomeTransaction)
async def create_income(
    income: schemas.IncomeTransactionCreate,
    db: Session = Depends(get_asset_db)
):
    """수익(배당/이자) 거래 생성"""
    return await crud.create_income_transaction(db=db, income=income)

@router.get("/", response_model=List[schemas.IncomeTransaction])
async def get_income_transactions(
    asset_id: Optional[int] = None,
    income_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_asset_db)
):
    """수익 거래 목록 조회"""
    return await crud.get_income_transactions(
        db=db,
        asset_id=asset_id,
        income_type=income_type,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )