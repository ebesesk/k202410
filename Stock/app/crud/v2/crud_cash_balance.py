from fastapi import HTTPException
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from app.models.investment_models import CashBalance
from app.schemas import investment_schemas_v2 as schemas
from app.utils.utils import get_current_kst_time



def update_cash_balance(
    db: Session,
    username: str,
    currency: str,
    amount: float,
    transaction_type: str,
    exchange_rate: float = None
):
    """현금 잔액 업데이트"""
    today = datetime.now().date()
    print('username update_cash_balance:', username)
    # 오늘 날짜의 잔액 레코드 조회
    cash_balance = db.query(CashBalance).filter(
        CashBalance.username == username,
        CashBalance.currency == currency,
        # CashBalance.date == today
    ).first()

    if not cash_balance:
        # 새 레코드 생성
        cash_balance = CashBalance(
            username=username,
            date=today,
            currency=currency,
            balance=0,
            total_invested=0,
            krw_invested=0,
            cash_metadata={
                'transactions': []
            }
        )
        db.add(cash_balance)
    
    # 잔액 업데이트
    if transaction_type == "DEPOSIT":
        cash_balance.balance += amount
        cash_balance.total_invested += amount
        if currency != 'KRW' and exchange_rate:
            cash_balance.krw_invested += (amount * exchange_rate)
        else:
            cash_balance.krw_invested += amount
    elif transaction_type == "WITHDRAWAL":
        cash_balance.balance -= amount
    
    try:
        db.flush()
        return cash_balance
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))