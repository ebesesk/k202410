from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.crud.v2 import crud_security_transaction as crud
from app.schemas import investment_schemas_v2
from typing import List

from app.utils.dependencies import get_investment_db, get_db
from app.utils.dependencies import get_current_user
from app.core.config import settings
from app.crud.trade import get_all_trade_log
from app.crud.v2 import crud_transactions as crud_transactions
from pprint import pprint


router = APIRouter(prefix="/transactions")


@router.post("/update-transaction")
def update_transaction(
    transaction: investment_schemas_v2.TransactionDict,
    db: Session = Depends(get_investment_db),
    current_user = Depends(get_current_user)
):
    # print('transaction.type:', transaction.type)
    crud_transactions.update_transaction(db, transaction, current_user["username"])


@router.get("/get-old-trade-log")
def get_old_trade_log(
    db: Session = Depends(get_investment_db),
    db_stock: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    
    crud_transactions.get_old_trade_log(db, db_stock, current_user["username"])



@router.get("/get-transactions-all")
def get_transactions_all(
    request: Request,
    keyword: str = None,
    date: str = None,
    skip: int = 0,
    limit: int = 20,
    db_investment: Session = Depends(get_investment_db),
    db_stock: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    key = request.headers.get('X-API-KEY')


    transactions = crud_transactions.get_transactions_all(
        key=key, 
        keyword=keyword,
        skip=skip, 
        limit=limit, 
        db_investment=db_investment, 
        db_stock=db_stock, 
        username=current_user["username"]
    )

    analyze_currency = crud_transactions.analyze_transactions_by_currency(db_investment, current_user["username"])
    # pprint(analyze_currency)
    fifo_summary = crud_transactions.get_asset_summary(key, date, db_investment, db_stock, current_user["username"])

    result = {
        'items': {
            'assetRealAmount': transactions['assetRealAmount'],
            'transactions': transactions['items'],
            'analyze_currency': analyze_currency,
            'fifo_summary': fifo_summary
        },
        'pagination': transactions['pagination']
    }
    
    return result
   


@router.get("/get-periodic-returns")
def get_periodic_returns(
    period: str = 'monthly',
    db_investment: Session = Depends(get_investment_db),
    current_user = Depends(get_current_user)
):
    result = crud_transactions.calculate_periodic_returns(db_investment, current_user["username"], period)
    return result


@router.get("/get-periodic-returns-v2")
def get_periodic_returns_v2(
    # period: str = 'monthly',
    db_investment: Session = Depends(get_investment_db),
    current_user = Depends(get_current_user)
):
    result = crud_transactions.calculate_periodic_returns_v2(db_investment, current_user["username"])
    return result






# @router.get("/get-transactions-by-type")
# def get_transactions_by_type(
#     request: Request,
#     type: str,
#     db_investment: Session = Depends(get_investment_db),
#     db_stock: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     result = crud_transactions.get_transactions_by_type(db_investment, current_user["username"], type)
#     return result

