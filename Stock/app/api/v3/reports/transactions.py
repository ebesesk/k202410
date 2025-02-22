from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date
from app.db.session import get_asset_db
from app.crud.v3 import reports as crud

router = APIRouter()

@router.get("/summary", response_model=List[Dict[str, Any]])
async def get_transaction_summary(
    start_date: date,
    end_date: date,
    group_by: str = Query(..., description="daily/monthly/asset_type/account"),
    transaction_type: Optional[str] = None,
    db: Session = Depends(get_asset_db)
):
    """거래 내역 요약"""
    return await crud.get_transaction_summary(
        db=db,
        start_date=start_date,
        end_date=end_date,
        group_by=group_by,
        transaction_type=transaction_type
    )

@router.get("/cash-flow", response_model=List[Dict[str, Any]])
async def get_cash_flow_report(
    start_date: date,
    end_date: date,
    account_id: Optional[int] = None,
    interval: str = Query("daily", description="daily/monthly"),
    db: Session = Depends(get_asset_db)
):
    """현금 흐름 보고서"""
    return await crud.get_cash_flow_report(
        db=db,
        start_date=start_date,
        end_date=end_date,
        account_id=account_id,
        interval=interval
    )

@router.get("/income", response_model=List[Dict[str, Any]])
async def get_income_report(
    start_date: date,
    end_date: date,
    income_type: Optional[str] = None,
    group_by: str = Query("monthly", description="daily/monthly/asset"),
    db: Session = Depends(get_asset_db)
):
    """수익(배당/이자) 보고서"""
    return await crud.get_income_report(
        db=db,
        start_date=start_date,
        end_date=end_date,
        income_type=income_type,
        group_by=group_by
    )

@router.get("/tax", response_model=List[Dict[str, Any]])
async def get_tax_report(
    year: int = Query(..., ge=2000, le=2100),
    transaction_type: Optional[str] = None,
    db: Session = Depends(get_asset_db)
):
    """세금 보고서"""
    return await crud.get_tax_report(
        db=db,
        year=year,
        transaction_type=transaction_type
    )

@router.get("/fees", response_model=List[Dict[str, Any]])
async def get_fee_report(
    start_date: date,
    end_date: date,
    fee_type: Optional[str] = None,
    group_by: str = Query("monthly", description="daily/monthly/type"),
    db: Session = Depends(get_asset_db)
):
    """수수료 보고서"""
    return await crud.get_fee_report(
        db=db,
        start_date=start_date,
        end_date=end_date,
        fee_type=fee_type,
        group_by=group_by
    )