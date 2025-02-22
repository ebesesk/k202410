# crud/v2/crud_income_transaction.py
from sqlalchemy.orm import Session
from app.schemas import investment_schemas_v2
from sqlalchemy.orm.attributes import flag_modified
from app.models.investment_models import Transaction
from datetime import datetime
from app.utils.utils import convert_to_kst
from app.crud.v2 import crud_cash_balance as crud_cash_balance
from app.crud.v2 import crud_asset as crud_asset
from app.crud.v2 import crud_account as crud_account

def datetime_to_str(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

def db_create_expense_transaction(
    db: Session,
    transaction: investment_schemas_v2.ExpenseTransactionCreate,
    username: str
) -> Transaction:
    
    """비용 거래 DB 생성"""
    
    print('transaction', transaction)
    if transaction.asset_id:
        asset = crud_asset.get_asset_by_id(db, transaction.asset_id, username)
        asset_type = asset.type.upper()
    else:
        asset_type = ''
    
    # 비용 거래 생성
    expense_transaction = Transaction(
        date=transaction.date,
        asset_id=transaction.asset_id,
        type=(asset_type+'_EXPENSE' if asset_type else 'EXPENSE'),
        currency=transaction.currency,
        amount=transaction.amount,
        debit_account_id=transaction.debit_account_id,
        credit_account_id=transaction.credit_account_id,
        note=transaction.note,
        transaction_metadata={},
        username=username,
    )
    db.add(expense_transaction)
    db.flush()

    # # 이익잉여금 반영
    # retained_expense = Transaction(
    #     date=transaction.date,
    #     asset_id=transaction.asset_id,
    #     type=(asset_type + '_EXPENSE_RETAINED' if asset_type else 'EXPENSE_RETAINED'),
    #     amount=transaction.amount,
    #     currency=transaction.currency,
    #     debit_account_id=crud_account.get_account_by_code(db, "3002", username).id, # 이익잉여금 계정
    #     credit_account_id=transaction.debit_account_id, # 비용 계정
    #     username=username,
    #     transaction_metadata={
    #         'income_transaction_id': expense_transaction.id,
    #     }
    # )
    # db.add(retained_expense)
    # db.flush()

    # expense_transaction.transaction_metadata['expense_transaction_id'] = retained_expense.id
    flag_modified(expense_transaction, "transaction_metadata")
    
    db.commit()
    db.refresh(expense_transaction)
    
