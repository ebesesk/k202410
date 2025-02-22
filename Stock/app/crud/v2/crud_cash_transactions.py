from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import func, and_
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.models.investment_models import Transaction, Position, Portfolio
from app.schemas import investment_schemas_v2 as schemas
from app.crud.v2 import crud_cash_balance as crud_cash_balance
from app.utils.utils import get_current_kst_time
# 현금 거래 생성
def create_cash_transaction(
        db: Session, 
        transaction: schemas.CashTransactionCreate,
        username: str
    ):
    print('username', username) 
    print('create_cash_transaction', transaction)
    # 1. 거래 내역 생성
    db_transaction = Transaction(
        date=transaction.date,
        type=transaction.type,
        currency=transaction.currency,
        amount=transaction.amount,
        debit_account_id=transaction.debit_account_id,
        credit_account_id=transaction.credit_account_id,
        note=transaction.note,
        username=username
    )
    print('db_transaction', db_transaction.username)
    db.add(db_transaction)
    db.flush()  # 메인 거래 먼저 flush하여 ID 생성
     
    # 2. 수수료 처리
    if transaction.fees:
        fee_transaction_ids = []
        for fee_code, fee_data in transaction.fees.items():
            fee_transaction = Transaction(
                date=transaction.date,
                type="FEE",
                currency=fee_data.get('currency', transaction.currency),
                amount=fee_data['amount'],
                debit_account_id=int(fee_code),
                credit_account_id=transaction.credit_account_id,
                note=f"거래 수수료: {fee_data.get('name', '')}",
                username=username,
                transaction_metadata={
                    'main_transaction_id': db_transaction.id,  # 이제 db_transaction.id가 유효함
                    'fee_type': 'CASH_TRANSACTION_FEE'
                }
            )
            db.add(fee_transaction)
            db.flush()  # 각 수수료 거래도 flush하여 ID 생성
            fee_transaction_ids.append(fee_transaction.id)

            # 수수료에 대한 현금 잔액 감소
            crud_cash_balance.update_cash_balance(
                db=db,
                username=username,
                currency=fee_data.get('currency', transaction.currency),
                amount=fee_data['amount'],
                transaction_type="WITHDRAWAL"
            )

        # 수수료 거래 ID들을 메인 거래의 메타데이터에 추가
        if db_transaction.transaction_metadata is None:
            db_transaction.transaction_metadata = {}
        db_transaction.transaction_metadata['fee_transactions'] = fee_transaction_ids
        flag_modified(db_transaction, "transaction_metadata")  # db_transaction 객체에 대해 flag_modified 호출

    db.flush()
    
    # 3. Position 업데이트 (현금 포지션)
    crud_cash_balance.update_cash_balance(
        db=db,
        username=username,
        currency=transaction.currency,
        amount=transaction.amount,
        transaction_type=transaction.type
    )
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction







# 현금 포지션 업데이트
def update_cash_position(db: Session, username: str, currency: str, amount: float, transaction_type: str):
    position = db.query(Position).filter(
        Position.username == username,
        Position.currency == currency,
        Position.asset_id.is_(None)  # 현금 포지션
    ).first()
    
    if not position:
        position = Position(
            username=username,
            currency=currency,
            quantity=0,
            asset_id=None
        )
        db.add(position)
    
    # 입금/출금에 따른 현금 포지션 업데이트
    if transaction_type == "DEPOSIT":
        position.quantity += amount
    elif transaction_type == "WITHDRAWAL":
        position.quantity -= amount






























