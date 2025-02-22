from fastapi import HTTPException
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm import Session
from sqlalchemy import and_, case, func, or_
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from app.models.investment_models import Account, Transaction
from app.schemas import investment_schemas_v2 as schemas
from app.utils.utils import get_current_kst_time

def get_account_id(db: Session, account_name: str):
    return db.query(Account).filter(Account.name == account_name).first().id

def get_account_by_id(db: Session, account_id: int, username: str):
    return db.query(Account).filter(Account.id == account_id, Account.username == username).first()

def get_account_by_code(db: Session, account_code: str, username: str):
    return db.query(Account).filter(Account.code == account_code, Account.username == username).first()

def get_code_by_id(db: Session, account_id: int, username: str):
    return db.query(Account).filter(Account.id == account_id, Account.username == username).first().code

def get_account_balance(db: Session, account_id: int, username: str) -> float:
    """
    계정의 잔액 계산
    - 자산, 비용 계정: 차변 - 대변
    - 부채, 자본, 수익 계정: 대변 - 차변
    """
    result = db.query(
        Account.code,
        func.sum(case(
            (Transaction.debit_account_id == account_id, Transaction.amount),
            else_=0
        )).label('debit_total'),
        func.sum(case(
            (Transaction.credit_account_id == account_id, Transaction.amount),
            else_=0
        )).label('credit_total')
    ).join(
        Transaction,
        or_(
            Transaction.debit_account_id == account_id,
            Transaction.credit_account_id == account_id
        )
    ).filter(
        Transaction.username == username,
        Account.id == account_id
    ).group_by(
        Account.code
    ).first()
    
    if not result:
        return 0
        
    # 계정 성격에 따라 잔액 계산 방식이 다름
    if result.code.startswith(('1', '4')):  # 자산, 비용 계정
        return float(result.debit_total - result.credit_total)
    else:  # 부채, 자본, 수익 계정
        return float(result.credit_total - result.debit_total)

def get_accounts_by_transaction(db: Session, username: str):
    """트랜잭션에 따른 계정 조회"""
    transactions = db.query(Transaction).filter(Transaction.username == username).all()
    
    accounts = []
    for tx in transactions:
        if tx.debit_account not in accounts:
            accounts.append(tx.debit_account)
        if tx.credit_account not in accounts:
            accounts.append(tx.credit_account)
    return accounts
