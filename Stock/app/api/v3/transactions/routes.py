from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.db.session import get_asset_db
from app.schemas import investment_schemas_v3 as schemas
from app.crud.v3 import transactions as crud

router = APIRouter()

@router.post("/", response_model=schemas.Transaction)
async def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_asset_db)
):
    """기본 거래 생성"""
    return await crud.create_transaction(db=db, transaction=transaction)

@router.get("/", response_model=List[schemas.Transaction])
async def get_transactions(
    transaction_type: Optional[schemas.TransactionType] = None,
    currency: Optional[str] = None,
    status: Optional[schemas.TransactionStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = None,
    group_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_asset_db)
):
    """거래 목록 조회"""
    return await crud.get_transactions(
        db=db,
        transaction_type=transaction_type,
        currency=currency,
        status=status,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        group_id=group_id,
        skip=skip,
        limit=limit
    )

@router.get("/{transaction_id}", response_model=schemas.Transaction)
async def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_asset_db)
):
    """특정 거래 상세 조회"""
    transaction = await crud.get_transaction(db=db, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.put("/{transaction_id}", response_model=schemas.Transaction)
async def update_transaction(
    transaction_id: int,
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_asset_db)
):
    """거래 정보 수정"""
    updated_transaction = await crud.update_transaction(
        db=db,
        transaction_id=transaction_id,
        transaction=transaction
    )
    if not updated_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return updated_transaction

@router.delete("/{transaction_id}", response_model=schemas.Transaction)
async def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_asset_db)
):
    """거래 삭제"""
    transaction = await crud.delete_transaction(db=db, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.get("/summary/daily", response_model=List[Dict[str, Any]])
async def get_daily_transaction_summary(
    start_date: datetime,
    end_date: datetime,
    transaction_type: Optional[schemas.TransactionType] = None,
    currency: Optional[str] = None,
    db: Session = Depends(get_asset_db)
):
    """일별 거래 요약"""
    return await crud.get_daily_transaction_summary(
        db=db,
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type,
        currency=currency
    )

@router.get("/summary/monthly", response_model=List[Dict[str, Any]])
async def get_monthly_transaction_summary(
    year: int = Query(..., ge=2000, le=2100),
    transaction_type: Optional[schemas.TransactionType] = None,
    currency: Optional[str] = None,
    db: Session = Depends(get_asset_db)
):
    """월별 거래 요약"""
    return await crud.get_monthly_transaction_summary(
        db=db,
        year=year,
        transaction_type=transaction_type,
        currency=currency
    )

@router.post("/batch", response_model=List[schemas.Transaction])
async def create_batch_transactions(
    transactions: List[schemas.TransactionCreate],
    db: Session = Depends(get_asset_db)
):
    """여러 거래 일괄 생성"""
    return await crud.create_batch_transactions(db=db, transactions=transactions)

@router.get("/search", response_model=List[schemas.Transaction])
async def search_transactions(
    query: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_asset_db)
):
    """거래 검색 (메모, 설명 등)"""
    return await crud.search_transactions(
        db=db,
        query=query,
        skip=skip,
        limit=limit
    )