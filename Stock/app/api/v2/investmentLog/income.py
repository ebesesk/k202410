# api/v2/investmentLog/income_transactions.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict
from app.schemas import investment_schemas_v2
from app.crud.v2 import crud_income as crud
from app.utils.dependencies import get_investment_db
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/income", tags=["income"])

@router.post("")
def create_income_transaction(
    transaction: investment_schemas_v2.IncomeTransactionCreate,
    db: Session = Depends(get_investment_db),
    current_user: dict = Depends(get_current_user)
):
    """수익 거래 생성 (배당, 이자 등)"""
    crud.db_create_income_transaction(
        db, 
        transaction, 
        current_user['username']
    )
    # print(current_user['username'])
    return {"message": "수익 거래 생성 완료"}