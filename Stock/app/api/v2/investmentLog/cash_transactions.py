from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.v2 import crud_cash_transactions as crud
from app.schemas import investment_schemas_v2


from app.utils.dependencies import get_investment_db
from app.utils.dependencies import get_current_user
from app.core.config import settings
base_accounts = settings.BASE_ACCOUNTS


router = APIRouter(prefix="/cash", tags=["cash_transactions"])


@router.post("", response_model=investment_schemas_v2.CashTransactionResponse)
def create_cash_transaction(
    transaction: investment_schemas_v2.CashTransactionCreate,
    db: Session = Depends(get_investment_db),
    current_user = Depends(get_current_user)
):
    # print('current_user', current_user['username'])
    return crud.create_cash_transaction(
        db=db, 
        transaction=transaction,
        username=current_user["username"]
    )
 

















