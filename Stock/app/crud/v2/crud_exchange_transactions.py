from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy import and_

from app.models.investment_models import Transaction, Position, ExchangeRate
from app.schemas import investment_schemas_v2 as schemas
from app.crud.v2 import crud_cash_transactions as crud_cash_transactions



def create_exchange_rate_transaction(db: Session, exchange_rate: schemas.ExchangeRateTransactionCreate, username: str) -> ExchangeRate:
    db_exchange_rate = Transaction(
        date=exchange_rate.date,
        type=exchange_rate.type,
        currency=exchange_rate.currency,
        amount=exchange_rate.amount,
        quantity=exchange_rate.quantity,
        exchange_rate=exchange_rate.exchange_rate,
        note=exchange_rate.note,
        debit_account_id=exchange_rate.debit_account_id,
        credit_account_id=exchange_rate.credit_account_id,
        fees=exchange_rate.fees,
        transaction_metadata=exchange_rate.transaction_metadata,
        username=username
    )
    db.add(db_exchange_rate)
    db.flush()
    
    # 원본 통화 출금 처리
    db_exchange_from_currency = schemas.CashTransactionCreate(
        date=exchange_rate.date,
        type='DEPOSIT',
        currency=exchange_rate.currency,
        amount=exchange_rate.amount,
        # note=exchange_rate.note,
        username=username,
        debit_account_id=7, # 원본
        credit_account_id=exchange_rate.credit_account_id,
        fees=exchange_rate.fees,
        transaction_metadata={
            'transactions_id': db_exchange_rate.id
        },
    )
    db_exchange_from_currency = crud_cash_transactions.create_cash_transaction(db, db_exchange_from_currency, username)
    
    
    # 대상 통화 입금 처리
    db_exchange_to_currency = schemas.CashTransactionCreate(
        date=exchange_rate.date,
        type='WITHDRAWAL',
        currency=exchange_rate.note,
        amount=exchange_rate.quantity,    
        # note=exchange_rate.note,
        username=username,
        debit_account_id=exchange_rate.debit_account_id,
        credit_account_id=7, # 원본
        fees=exchange_rate.fees,
        transaction_metadata={
            'transactions_id': db_exchange_rate.id
        },
    )
    db_exchange_to_currency = crud_cash_transactions.create_cash_transaction(db, db_exchange_to_currency, username)
   
    
    db_exchange_rate.transaction_metadata['transactions_id'] = {
        'from_currency': db_exchange_from_currency.id,
        'to_currency': db_exchange_to_currency.id
    }
    flag_modified(db_exchange_rate, 'transaction_metadata')
    
    db.commit()
    db.refresh(db_exchange_rate)
    
    return db_exchange_rate






def create_exchange_rate(db: Session, exchange_rate: schemas.ExchangeRateCreate) -> ExchangeRate:
    db_exchange_rate = ExchangeRate(
        from_currency=exchange_rate.from_currency,
        to_currency=exchange_rate.to_currency,
        rate=exchange_rate.rate,
        date=exchange_rate.date,
        source=exchange_rate.source,
        username=exchange_rate.username
    )
    db.add(db_exchange_rate)
    db.commit()
    db.refresh(db_exchange_rate)
    return db_exchange_rate

def get_exchange_rate(
    db: Session, 
    from_currency: str, 
    to_currency: str, 
    date: Optional[datetime] = None,
    username: str = None
) -> Optional[ExchangeRate]:
    query = db.query(ExchangeRate).filter(
        and_(
            ExchangeRate.from_currency == from_currency,
            ExchangeRate.to_currency == to_currency,
            ExchangeRate.username == username
        )
    )
    
    if date:
        query = query.filter(ExchangeRate.date <= date)
        return query.order_by(ExchangeRate.date.desc()).first()
    
    return query.order_by(ExchangeRate.date.desc()).first()

def get_exchange_rates(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    username: str = None
) -> List[ExchangeRate]:
    return db.query(ExchangeRate)\
        .filter(ExchangeRate.username == username)\
        .order_by(ExchangeRate.date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def update_exchange_rate(
    db: Session,
    exchange_rate_id: int,
    exchange_rate: schemas.ExchangeRateUpdate,
    username: str
) -> Optional[ExchangeRate]:
    db_exchange_rate = db.query(ExchangeRate)\
        .filter(
            and_(
                ExchangeRate.id == exchange_rate_id,
                ExchangeRate.username == username
            )
        )\
        .first()
    
    if not db_exchange_rate:
        return None
    
    update_data = exchange_rate.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_exchange_rate, field, value)
    
    db.commit()
    db.refresh(db_exchange_rate)
    return db_exchange_rate

def delete_exchange_rate(
    db: Session, 
    exchange_rate_id: int,
    username: str
) -> bool:
    db_exchange_rate = db.query(ExchangeRate)\
        .filter(
            and_(
                ExchangeRate.id == exchange_rate_id,
                ExchangeRate.username == username
            )
        )\
        .first()
    
    if not db_exchange_rate:
        return False
    
    db.delete(db_exchange_rate)
    db.commit()
    return True

def get_latest_rates(
    db: Session,
    username: str,
    currencies: Optional[List[str]] = None
) -> dict:
    """특정 통화들의 최신 환율 정보를 가져옴"""
    query = db.query(ExchangeRate)\
        .filter(ExchangeRate.username == username)
    
    if currencies:
        query = query.filter(ExchangeRate.from_currency.in_(currencies))
    
    # 각 통화 쌍의 최신 환율만 선택
    latest_rates = {}
    results = query.order_by(ExchangeRate.date.desc()).all()
    print('results:', results)
    for rate in results:
        _key = rate.from_currency
        if _key not in latest_rates:
            latest_rates[_key] = {
                rate.to_currency : {
                    "rate": rate.rate,
                    "date": rate.date,
                }
            }
    
    # lates_rates = {
    #     'USD': {
    #         'KRW': {
        # },
    #         'rate': 1000,
    #         'date': '2024-01-01',
    #     }
    # }
    
    print('latest_rates:', latest_rates)
    return latest_rates


def get_currencies(db: Session, username: str):
    """날짜별 화폐 조회"""
    currencies = db.query(Transaction.currency).filter(Transaction.username == username).distinct().all()
    return [currency[0] for currency in currencies]