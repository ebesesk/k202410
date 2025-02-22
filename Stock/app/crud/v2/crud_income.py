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

def db_create_income_transaction(
    db: Session,
    transaction: investment_schemas_v2.IncomeTransactionCreate,
    username: str
) -> Transaction:
    
    """수익 거래 DB 생성"""
    
    print('transaction', transaction)
    
    if transaction.asset_id:
        asset = crud_asset.get_asset_by_id(db, transaction.asset_id, username)
        asset_type = asset.type.upper()
    else:
        asset_type = ''
    
    
    # 수익 거래 생성
    income_transaction = Transaction(
        date=transaction.date,
        asset_id=transaction.asset_id,
        type=(asset_type + '_INCOME' if asset_type else 'INCOME'),
        currency=transaction.currency,
        amount=transaction.amount,
        debit_account_id=transaction.debit_account_id,  # 현금성자산 증가   
        credit_account_id=transaction.credit_account_id,  # 수익 자산 증가
        note=transaction.note,
        fees=transaction.fees,
        transaction_metadata={
            'transactions_id': [],
        },
        username=username,
    )
    db.add(income_transaction)
    db.flush()
    
    # # 이익잉여금 반영
    # retained_income = Transaction(
    #     date=transaction.date,
    #     asset_id=transaction.asset_id,
    #     type=(asset_type + '_INCOME_RETAINED' if asset_type else 'INCOME_RETAINED'),
    #     amount=transaction.amount,
    #     currency=transaction.currency,
    #     debit_account_id=transaction.credit_account_id,  # 수익 자산 감소
    #     credit_account_id=crud_account.get_account_by_code(db, "3002", username).id,  # 이익잉여금 증가
    #     username=username,
    #     transaction_metadata={
    #         'transactions_id': income_transaction.id,
    #     }
    # )
    # db.add(retained_income)
    # db.flush()
    
    # # 수익 거래 반영
    # crud_cash_balance.update_cash_balance(
    #     db=db,
    #     username=username,
    #     currency=transaction.currency,
    #     amount=transaction.amount,
    #     transaction_type=(asset_type + "_DEPOSIT" if asset_type else "DEPOSIT"),
    #     # exchange_rate=transaction.exchange_rate
    # )
    
    if transaction.fees:
        fee_transactions = []
        # 수수료 거래 생성
        for fee_code, fee_data in transaction.fees.items():
            fee_transaction = Transaction(
                date=convert_to_kst(transaction.date),
                asset_id=transaction.asset_id,
                type=(asset_type + '_INCOME_FEE' if asset_type else 'INCOME_FEE'),
                currency=transaction.currency,
                amount=fee_data['amount'],
                debit_account_id=fee_data['id'],
                credit_account_id=transaction.debit_account_id,
                note=f"거래 수수료: {fee_data['name']}",
                transaction_metadata={
                    'transactions_id': income_transaction.id,
                },
                username=username,
            )
            db.add(fee_transaction)
            db.flush()
            fee_transactions.append(fee_transaction.id)
            
            
            # # 이익잉여금 반영
            # retained_fee = Transaction(
            #     date=transaction.date,
            #     asset_id=transaction.asset_id,
            #     type=(asset_type + '_INCOME_FEE_RETAINED' if asset_type else 'INCOME_FEE_RETAINED'),
            #     amount=fee_data['amount'],
            #     currency=fee_data['currency'],
            #     debit_account_id=crud_account.get_account_by_code(db, "3002", username).id,
            #     credit_account_id=fee_data['id'],
            #     username=username,
            #     transaction_metadata={
            #         'transactions_id': income_transaction.id,
            #     }
            # )
            # db.add(retained_fee)
            # db.flush()
            
            # fee_transactions.append(retained_fee.id)
            
            
            print('fee_transaction', fee_transaction)
            print('fee_transaction', fee_transaction.debit_account_id)
            fee_transactions.append(fee_transaction.id)
            
            # crud_cash_balance.update_cash_balance(
            #     db=db,
            #     username=username,
            #     currency=fee_transaction.currency,
            #     amount=fee_transaction.amount,
            #     transaction_type=asset_type + "_WITHDRAWAL",
            #     # exchange_rate=transaction.exchange_rate
            # )
        # db.flush()
        # income_transaction.transaction_metadata['transactions_id'].append(retained_income.id)
        income_transaction.transaction_metadata['transactions_id'].extend(list(set(fee_transactions)))
        flag_modified(income_transaction, "transaction_metadata")

    db.commit()
    db.refresh(income_transaction)
     