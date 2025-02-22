from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
from app.utils.dependencies import get_investment_db
from app.utils.dependencies import get_current_user

from app.crud.v2 import crud_exchange_transactions as crud
from app.schemas import investment_schemas_v2 as schemas

from app.core.config import settings
base_accounts = settings.BASE_ACCOUNTS











router = APIRouter(prefix="/exchange")


@router.post("/transactions", response_model=schemas.ExchangeRateTransactionResponse)
async def create_exchange_rate_transaction(
    *,
    db: Session = Depends(get_investment_db),
    exchange_rate_in: schemas.ExchangeRateTransactionCreate,
    current_user = Depends(get_current_user)
):
    """
    환율 트랜잭션 생성
    """
    exchange_rate_in.username = current_user["username"]
    return crud.create_exchange_rate_transaction(db, exchange_rate_in, current_user["username"])


@router.post("", response_model=schemas.ExchangeRateInDB)
async def create_exchange_rate(
    *,
    db: Session = Depends(get_investment_db),
    exchange_rate_in: schemas.ExchangeRateCreate,
    current_user = Depends(get_current_user)
):
    """
    새로운 환율 정보 생성
    """
    exchange_rate_in.username = current_user["username"]
    return crud.create_exchange_rate(db, exchange_rate_in)

@router.get("/latest", response_model=dict)
async def get_latest_rates(
    *,
    db: Session = Depends(get_investment_db),
    current_user = Depends(get_current_user),
    # currencies: Optional[List[str]] = Query(None)
):
    """
    최신 환율 정보 조회
    """
    return crud.get_latest_rates(db, current_user["username"])

@router.get("/{from_currency}/{to_currency}", response_model=schemas.ExchangeRateInDB)
async def get_specific_exchange_rate(
    *,
    db: Session = Depends(get_investment_db),
    from_currency: str,
    to_currency: str,
    date: Optional[datetime] = None,
    current_user = Depends(get_current_user)
):
    """
    특정 통화 쌍의 환율 조회
    """
    exchange_rate = crud.get_exchange_rate(
        db, from_currency, to_currency, date, current_user
    )
    if not exchange_rate:
        raise HTTPException(
            status_code=404,
            detail=f"Exchange rate for {from_currency}/{to_currency} not found"
        )
    return exchange_rate

@router.get("/", response_model=List[schemas.ExchangeRateInDB])
async def list_exchange_rates(
    *,
    db: Session = Depends(get_investment_db),
    current_user = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    환율 목록 조회
    """
    return crud.get_exchange_rates(db, skip, limit, current_user)

@router.put("/{exchange_rate_id}", response_model=schemas.ExchangeRateInDB)
async def update_exchange_rate(
    *,
    db: Session = Depends(get_investment_db),
    exchange_rate_id: int,
    exchange_rate_in: schemas.ExchangeRateUpdate,
    current_user = Depends(get_current_user)
):
    """
    환율 정보 수정
    """
    exchange_rate = crud.update_exchange_rate(
        db, exchange_rate_id, exchange_rate_in, current_user
    )
    if not exchange_rate:
        raise HTTPException(
            status_code=404,
            detail=f"Exchange rate with id {exchange_rate_id} not found"
        )
    return exchange_rate

@router.delete("/{exchange_rate_id}")
async def delete_exchange_rate(
    *,
    db: Session = Depends(get_investment_db),
    exchange_rate_id: int,
    current_user = Depends(get_current_user)
):
    """
    환율 정보 삭제
    """
    success = crud.delete_exchange_rate(db, exchange_rate_id, current_user)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Exchange rate with id {exchange_rate_id} not found"
        )
    return {"message": "Exchange rate successfully deleted"}

@router.get("/history/{from_currency}/{to_currency}", response_model=List[schemas.ExchangeRateInDB])
async def get_exchange_rate_history(
    *,
    db: Session = Depends(get_investment_db),
    from_currency: str,
    to_currency: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user = Depends(get_current_user)
):
    """
    특정 통화 쌍의 환율 이력 조회
    """
    return crud.get_exchange_rate_history(
        db, from_currency, to_currency, start_date, end_date, current_user
    )