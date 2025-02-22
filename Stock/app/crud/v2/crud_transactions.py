from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import func, and_, cast, Float, JSON, text, Float, case, func, or_, extract
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from calendar import monthrange

from app.models.investment_models import (Transaction, 
                                          Position, 
                                          Portfolio, 
                                          Account,
                                          Asset)
from app.schemas import investment_schemas_v2 as schemas
from app.crud.v2 import crud_cash_balance as crud_cash_balance

from app.utils.utils import get_current_kst_time, convert_to_kst
from app.crud.v2 import crud_position_transaction as crud_position
from app.crud.v2 import crud_account as crud_account
from app.crud.v2 import crud_asset as crud_asset
from app.models.investment_models import Transaction

from app.crud import stock as crud_stock
from app.utils.dependencies import get_investment_db, get_db
from app.schemas import investment_schemas_v2 as schemas
from app.crud.trade import get_all_trade_log as get_all_old_trade_log
from app.crud.v2 import crud_security_transaction as crud_security_transaction  
from app.crud.v2 import crud_asset as crud_asset
from app.crud.v2 import crud_income as crud_income
from app.crud.v2 import crud_transactions as crud_transactions
from app.crud.v2 import crud_exchange_transactions as crud_exchange
from app.crud.v2 import crud_account as crud_account
from app.utils.utils import get_multi_t8407
from app.utils.fdr_util import get_fdr_price
from app.utils.utils import compare_dict

from app.core.config import settings

from pprint import pprint


def del_transaction_by_id(db, transaction_id, username):
    _delete = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.username == username
    ).first()
    if _delete:
        db.delete(_delete)
        db.commit()
        return True
    else:
        return False


def get_all_transaction_by_asset_id(db, asset_id, username):
    sell_transaction = db.query(Transaction).filter(
        Transaction.username == username,
        # Transaction.type.endswith('SELL'),
        Transaction.asset_id == asset_id
    ).all()
    return sell_transaction


def get_transaction_by_id(db, transaction_id, username):
    # print('transaction_id:', transaction_id)
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.username == username
    ).first()
    # print('transaction:', transaction.id, transaction.date, transaction.type, crud_asset.get_asset_by_id(db, transaction.asset_id, username).name)
    return transaction

def get_total_fee(db, transaction, username):
    fees = 0
    for _key, _value in transaction.fees.items():
        fees += _value['amount']
    return fees

def get_total_fees_dict(db, transaction, username):
    fees = {}
    for _key, _value in transaction.fees.items():
        if _value['amount'] == 0:
            continue
        else:
            fees[_key] = _value
    return fees

def get_sell_transaction(db, transaction, username):
    
    # # if 'main_transaction' in transaction.transaction_metadata['fifo']:
    # print('transaction.transaction_metadata:', transaction.transaction_metadata)
    try:
        # 가장 오래된 매도 트랜잭션 조회
        sell_date = None
        for tx in transaction.transaction_metadata['fifo']['main_transaction']:
            if not sell_date:
                _tx = get_transaction_by_id(db, tx['id'], username)
                sell_date = _tx.date
            else:
                if _tx.date < sell_date:
                    sell_date = _tx.date
    except Exception as e:
        print('error:', e)
        sell_date = transaction.date
    if not sell_date:
        sell_date = transaction.date
    # sell_date = transaction.date
        
    print('======================')
    print('transaction:',transaction.id, transaction.date, crud_asset.get_asset_by_id(db, transaction.asset_id, username).name)
    print('sell_date:',sell_date)
    print('======================')
    
    asset_transaction = get_all_transaction_by_asset_id(db, transaction.asset_id, username)
    
    print('모든 트랜잭션 조회')
    for tx in asset_transaction:
        print('tx:', tx.id, tx.date, tx.type, crud_asset.get_asset_by_id(db, tx.asset_id, username).name)
    print('======================')
    
    buy_transaction = []
    sell_transaction = []
    for tx in asset_transaction:
        # 매수 날짜 이후 매도 트랜잭션 조회
        if tx.type.endswith('SELL') and tx.date >= sell_date:
            sell_transaction.append(tx)
        # 수정 매도 이후 모든 매도 트랜잭션 조회
        if tx.type.endswith('BUY') and tx.date >= transaction.date and tx.id != transaction.id:
            buy_transaction.append(tx)
    
    print('매도 트랜잭션 조회')
    for tx in sell_transaction:
        print('tx sell:', tx.id, crud_asset.get_asset_by_id(db, tx.asset_id, username).name)
    print('======================')
    print('매수 트랜잭션 조회')
    for tx in buy_transaction:
        print('tx buy:', tx.id, crud_asset.get_asset_by_id(db, tx.asset_id, username).name)
    print('======================')
    
    return sell_transaction, buy_transaction

    
   


def update_fifo(db, transaction, username):
    _transaction = get_transaction_by_id(db, transaction.id, username)
    _transaction.transaction_metadata['fifo']['quantity'] = transaction.quantity
    _transaction.transaction_metadata['fifo']['main_transaction'] = []
    db.add(_transaction)
    db.commit()
    db.refresh(_transaction)
    return _transaction

def update_fees_by_transactions_id(db, transaction, username):
    
    # FEE 관련 서브 트랜잭션 삭제
    _id_list = transaction.transaction_metadata['transactions_id'].copy()
    for _id in _id_list:
        _sub = get_transaction_by_id(db, _id, username)
        if _sub:
            print('서브 트랜잭션 존재:', _sub.id, _sub.type)
            if _sub.type.endswith('FEE'):
                print('서브 트랜잭션 삭제:', _sub.id)
                db.delete(_sub)
                db.flush()
                transaction.transaction_metadata['transactions_id'].remove(_sub.id)
        else:
            transaction.transaction_metadata['transactions_id'].remove(_id)
    # FEE 관련 서브 트랜잭션 생성
    transactions_id = []
    fees = {}
    for _key, _value in transaction.fees.items():
        if _value['amount'] == 0:
            continue
        # 없으면 추가
        else:
            if _key not in fees:
                fees[_key] = {}
            fees[_key]['amount'] = _value['amount']
            fees[_key]['currency'] = _value['currency']
            fees[_key]['id'] = _value['id']
            fees[_key]['name'] = _value['name']
            fees[_key]['code'] = _value['code']
            db_fee = Transaction(
                date=transaction.date,
                asset_id=getattr(transaction, 'asset_id', None),
                type=transaction.type + '_FEE',
                currency=transaction.currency,
                amount=_value['amount'],
                transaction_metadata={'transactions_id': transaction.id},
                username=username,
                debit_account_id=_value['id'],
                credit_account_id=transaction.debit_account_id,
            )
            db.add(db_fee)
            db.flush()
            pprint(db_fee.__dict__)
            transactions_id.append(db_fee.id)
                
    transaction.transaction_metadata['transactions_id'].extend(transactions_id)
    # flag_modified(transaction, 'transaction_metadata')
    transaction.fees = fees
        
    # pprint(transaction.__dict__)
    # db.rollback()

    return transaction
     
def update_transaction_fields(db, db_transaction, transaction):
    print('=========================================================')
    pprint(transaction.__dict__)
    print('=========================================================')
    # None 제외 업데이트 필드 추출
    update_fields = {
        key: value for key, value in transaction.__dict__.items() 
        if value is not None and not key.startswith('_')
    }
    
    # 업데이트 필드 적용
    for key, value in update_fields.items():
        if hasattr(db_transaction, key):
            setattr(db_transaction, key, value)
            
    # 업데이트 적용
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction

def get_fees_by_transactions_id(db, transactions_id, username):
    fees = {}
    print('transactions_id:', transactions_id)
    for _id in transactions_id:
        _transaction = get_transaction_by_id(db, _id, username)
        if _transaction:
            account = crud_account.get_account_by_id(db, _transaction.debit_account_id, username)
            if account.code.startswith('4'):
                fees[account.code] = {
                    'amount': _transaction.amount,
                    'currency': _transaction.currency,
                    'id': _transaction.debit_account_id,
                    'name': account.name,
                    'code': account.code
                }
    return fees

def update_transaction(db, transaction, username):
    
    account_debit = crud_account.get_account_by_id(db, transaction.debit_account_id, username)
    account_credit = crud_account.get_account_by_id(db, transaction.credit_account_id, username)
    db_transaction = get_transaction_by_id(db, transaction.id, username)
    # db.commit()
    # db.refresh(db_transaction)
    
    
    if transaction.asset_id and transaction.type.endswith('SELL'):
        
        
        # print('is_same_fees:', is_same_fees)
        # 매수 트랜잭션 찾기기
        buy_transaction = None
        for tx in transaction.transaction_metadata['transactions_id']:
            # print('tx:', tx)
            _tx = get_transaction_by_id(db, tx, username)
            # pprint(_tx.__dict__)
            # print('tx:', _tx.id, _tx.date, _tx.quantity, _tx.type, crud_asset.get_asset_by_id(db, _tx.asset_id, username).name)
            if _tx.type.endswith('BUY'):
                print('buy_transaction:', _tx.id, _tx.date, _tx.quantity, _tx.type, crud_asset.get_asset_by_id(db, _tx.asset_id, username).name)
                if not buy_transaction:
                    buy_transaction = _tx
                else:
                    if buy_transaction.date > _tx.date:
                        buy_transaction = _tx
        print('buy_transaction:', buy_transaction.id, buy_transaction.date, buy_transaction.quantity, buy_transaction.type, crud_asset.get_asset_by_id(db, buy_transaction.asset_id, username).name)
    
        
        
        # 매도 트랜잭션 조회
        sell_transactions = []
        buy_transactions = []
        asset_transaction = get_all_transaction_by_asset_id(db, transaction.asset_id, username)
        
        # 매수 트랜잭션과 관련된 매도 트랜잭션 수집
        for tx in asset_transaction:
            if tx.type.endswith('BUY') and tx.date >= buy_transaction.date:
                buy_transactions.append(tx)
                for tx_id in tx.transaction_metadata['fifo']['main_transaction']:
                    # sell_transactions.append(tx_id)
                    print('sell_transactions:', tx_id['id'])
                    sell_transaction = get_transaction_by_id(db, tx_id['id'], username)
                    if sell_transaction:
                        sell_transactions.append(sell_transaction)
        # 중복 제거
        sell_transactions = list(set(sell_transactions))
        print('sell_transactions:', sell_transactions)
        print('buy_transactions:', buy_transactions)
        # sell_transactions, buy_transactions = get_sell_transaction(db, buy_transaction, username)
        
        # FIFO 초기화
        print('FIFO 초기화 ==========================')
        print('buy_transactions:', len(buy_transactions))       
        for tx in buy_transactions:
            # print('buy_transaction:', tx.id, crud_asset.get_asset_by_id(db, tx.asset_id, username).name)
            print('buy_transaction:', tx.id, tx.date,tx.quantity, tx.type, crud_asset.get_asset_by_id(db, tx.asset_id, username).name)
            tx.transaction_metadata['fifo']['quantity'] = tx.quantity
            tx.transaction_metadata['fifo']['main_transaction'] = []
            flag_modified(tx, 'transaction_metadata')
            print('tx:', tx.transaction_metadata)
            db.add(tx)
        
        db.flush()
         
        
        
        
        
        # 매도 스키마 생성
        sell_schema = []
        for tx in sell_transactions:
            # pprint(tx.__dict__)
            # print('======================')
            if tx.type.endswith('SELL') and tx.price:
                if tx.id == transaction.id:
                    _schema = schemas.SecurityTransactionCreate(
                        id=transaction.id,
                        date=transaction.date,
                        type=transaction.type,
                        currency=transaction.currency,
                        asset_id=transaction.asset_id,
                        quantity=transaction.quantity,
                        amount=transaction.amount,
                        price=transaction.amount / transaction.quantity,
                        fees=transaction.fees,
                        transaction_metadata={},
                        debit_account_id=transaction.debit_account_id,
                        credit_account_id=transaction.credit_account_id,
                        username=username,
                        # get_info=True
                    )
                else:
                    _schema = schemas.SecurityTransactionCreate(
                        id=tx.id,
                        date=tx.date,
                        type=tx.type,
                        currency=tx.currency,
                        asset_id=tx.asset_id,
                        quantity=tx.quantity,
                        amount=tx.transaction_metadata['sell_amount'],
                        price=tx.transaction_metadata['sell_price'],
                        fees=tx.fees,
                        transaction_metadata={},
                        debit_account_id=tx.debit_account_id,
                        credit_account_id=tx.credit_account_id,
                        username=username,
                        # get_info=True
                    )
                sell_schema.append(_schema)
                
                # 관련 트랜잭션 삭제제
                print('tx:', tx.transaction_metadata['transactions_id'])
                for tx_id in tx.transaction_metadata['transactions_id']:
                    print('tx_id:', tx_id)
                    _tx = get_transaction_by_id(db, tx_id, username)
                    if _tx and (_tx.type.endswith('FEE') or
                                _tx.type.endswith('PROFIT') or 
                                _tx.type.endswith('LOSS')):
                        print('tx_id:', tx_id, _tx.type)
                        del_transaction_by_id(db, tx_id, username)
                # tx.transaction_metadata = {}
                # flag_modified(tx, 'transaction_metadata')
                del_transaction_by_id(db, tx.id, username)
                # db.add(tx)
                # db.flush()
                # db.commit()
                # db.refresh(tx)
        db.commit()
        # db.refresh(tx)    
        # 날짜순 정렬 후 재생성
        _schema_list = sorted(sell_schema, key=lambda x: x.date)
        for _schema in _schema_list:
            crud_security_transaction.create_security_transaction_v2(db, _schema, username)
       
    
    
    
    elif transaction.asset_id and transaction.type.endswith('BUY'):
        
        total_fees = 0
        fees = {}
        for _key, _value in transaction.fees.items():
            if _value['amount'] == 0:
                continue
            else:
                total_fees += _value['amount']
                fees[_key] = _value
        
        db_transaction.date = transaction.date
        db_transaction.asset_id = transaction.asset_id
        db_transaction.type = transaction.type
        db_transaction.quantity = transaction.quantity
        db_transaction.price = (transaction.amount + total_fees) / transaction.quantity
        db_transaction.currency = transaction.currency
        db_transaction.amount = transaction.amount + total_fees
        db_transaction.username = username
        db_transaction.fees = fees
        db_transaction.debit_account_id = transaction.debit_account_id
        db_transaction.credit_account_id = transaction.credit_account_id
        db_transaction.transaction_metadata = {
            "fifo": {
                "quantity": transaction.quantity,
                "main_transaction": []
            }
        }        
        db.add(db_transaction)
        # db.flush()
        
        
        sell_transactions, buy_transactions = get_sell_transaction(db, db_transaction, username)
        # FIFO 초기화     
        for tx in buy_transactions:
            # print('buy_transaction:', tx.id, crud_asset.get_asset_by_id(db, tx.asset_id, username).name)
            print('buy_transaction:', tx.id, tx.date,tx.quantity, tx.type, crud_asset.get_asset_by_id(db, tx.asset_id, username).name)
            tx.transaction_metadata['fifo']['quantity'] = tx.quantity
            tx.transaction_metadata['fifo']['main_transaction'] = []
            flag_modified(tx, 'transaction_metadata')
            print('tx:', tx.transaction_metadata)
            db.add(tx)
            # db.flush()
            # db.commit()
            # db.refresh(tx)
        
        
        
        
        
        sell_schema = []
        for tx in sell_transactions:
            # pprint(tx.__dict__)
            # print('======================')
        
            _schema = schemas.SecurityTransactionCreate(
                id=tx.id,
                date=tx.date,
                type=tx.type,
                currency=tx.currency,
                asset_id=tx.asset_id,
                quantity=tx.quantity,
                amount=tx.transaction_metadata['sell_amount'],
                price=tx.transaction_metadata['sell_price'],
                fees=tx.fees,
                transaction_metadata={},
                debit_account_id=tx.debit_account_id,
                credit_account_id=tx.credit_account_id,
                username=username,
                # get_info=True
            )
            sell_schema.append(_schema)
            print('tx:', tx.transaction_metadata['transactions_id'])
            for tx_id in tx.transaction_metadata['transactions_id']:
                print('tx_id:', tx_id)
                _tx = get_transaction_by_id(db, tx_id, username)
                if _tx and (_tx.type.endswith('FEE') or _tx.type.endswith('PROFIT') or _tx.type.endswith('LOSS')):
                    print('tx_id:', tx_id, _tx.type)
                    del_transaction_by_id(db, tx_id, username)
            # tx.transaction_metadata = {}
            # flag_modified(tx, 'transaction_metadata')
            del_transaction_by_id(db, tx.id, username)
            # db.add(tx)
            db.flush()
            # db.commit()
            # db.refresh(tx)
        db.commit()
        # db.refresh(tx)    
        _schema_list = sorted(sell_schema, key=lambda x: x.date, reverse=False)
        for _schema in _schema_list:
            print('schema======================')
            pprint(_schema.__dict__)
            info = crud_security_transaction.create_security_transaction_v2(db, _schema, username)
            # print('info:', info)
    
    
    
        
        # db.rollback()
        # print('======================')
        # pprint(transaction.__dict__)
        # print('======================')
        # pprint(db_transaction.__dict__)
        # print('트랜잭션 업데이트 안함')
    

    
    
    
    
    
    elif transaction.asset_id and transaction.type.endswith('FEE'):
        
        account = crud_account.get_account_by_id(db, transaction.debit_account_id, username)
        # FEE 처리  
        if transaction.amount == 0:
            db.delete(db_transaction)
        else:
            db_transaction.date = transaction.date
            db_transaction.amount = transaction.amount
            db_transaction.currency = transaction.currency
            db_transaction.debit_account_id = transaction.debit_account_id
            db_transaction.credit_account_id = transaction.credit_account_id
            db.add(db_transaction)
            db.flush()
        
        # main fees 업데이트
        fees = {}
        fee_list = []
        main_transaction = get_transaction_by_id(db, db_transaction.transaction_metadata['transactions_id'], username)
        _id_list = main_transaction.transaction_metadata['transactions_id'].copy()
        for _id in _id_list:
            _sub = get_transaction_by_id(db, _id, username)
            if _sub:
                if _sub.type.endswith('FEE'):
                    fee_list.append(_sub.id)
                    if _sub.debit_account_id not in fees:
                        fees[_sub.debit_account_id] = {}
                    account = crud_account.get_account_by_id(db, _sub.debit_account_id, username)
                    fees[_sub.debit_account_id]['amount'] = _sub.amount
                    fees[_sub.debit_account_id]['currency'] = _sub.currency
                    fees[_sub.debit_account_id]['id'] = account.id
                    fees[_sub.debit_account_id]['name'] = account.name
                    fees[_sub.debit_account_id]['code'] = account.code
            else:
                main_transaction.transaction_metadata['transactions_id'].remove(_id)
        main_transaction.fees = fees
        main_transaction.transaction_metadata['transactions_id'].extend(fee_list)
        db.add(main_transaction)
        db.commit()
        db.refresh(main_transaction)
    
    
    
    elif transaction.type.endswith('EXCHANGE'):
        print('EXCHANGE')
        pprint(transaction.__dict__)
        
        db_transaction.date = transaction.date
        db_transaction.type = transaction.type
        db_transaction.currency = transaction.currency
        db_transaction.amount = transaction.amount
        db_transaction.quantity = transaction.quantity
        db_transaction.exchange_rate = transaction.exchange_rate
        db_transaction.note = transaction.note
        db_transaction.debit_account_id = transaction.debit_account_id
        db_transaction.credit_account_id = transaction.credit_account_id
        db_transaction.fees = transaction.fees
        db_transaction.transaction_metadata = transaction.transaction_metadata
        
        db.add(db_transaction)
        db.flush()
        pprint(db_transaction.transaction_metadata)
        db_exchange_from_currency = get_transaction_by_id(
            db, 
            db_transaction.transaction_metadata['transactions_id']['from_currency'], 
            username
        )
        if db_exchange_from_currency and db_exchange_from_currency.type.endswith('DEPOSIT'):
            db_exchange_from_currency.date = transaction.date
            # db_exchange_from_currency.type = 'DEPOSIT'
            db_exchange_from_currency.currency = transaction.currency
            db_exchange_from_currency.amount = transaction.amount
            db_exchange_from_currency.debit_account_id = 7
            db_exchange_from_currency.credit_account_id = transaction.credit_account_id
            
            
            # db_exchange_from_curren   cy.transaction_metadata = transaction.transaction_metadata
            # db_exchange_from_currency.fees = transaction.fees
            
            
            
            # db_exchange_from_currency.quantity = transaction.quantity
            # db_exchange_from_currency.exchange_rate = transaction.exchange_rate
            # db_exchange_from_currency.note = transaction.note
            # db_exchange_from_currency.username = username
            db.add(db_exchange_from_currency)
            db.flush()
        
        db_exchange_to_currency = get_transaction_by_id(
            db, 
            db_transaction.transaction_metadata['transactions_id']['to_currency'], 
            username)   
        if db_exchange_to_currency and db_exchange_to_currency.type.endswith('WITHDRAWAL'):
            db_exchange_to_currency.date = transaction.date
            # db_exchange_to_currency.type = 'WITHDRAWAL'
            db_exchange_to_currency.currency = transaction.note
            db_exchange_to_currency.amount = transaction.quantity
            db_exchange_to_currency.debit_account_id = transaction.debit_account_id
            db_exchange_to_currency.credit_account_id = 7
            db.add(db_exchange_to_currency)
            db.flush()
            
        db.commit()
        
        return db_transaction
    
    
    
    elif not account_debit.code.startswith('3') and  not account_credit.code.startswith('3'):
        if transaction.transaction_metadata and transaction.transaction_metadata['transactions_id']:
            fees = get_fees_by_transactions_id(db, transaction.transaction_metadata['transactions_id'], username)
            is_same_fees = compare_dict(transaction.fees, fees)
            if not is_same_fees:
                transaction = update_fees_by_transactions_id(db, transaction, username)
            
        return update_transaction_fields(db, db_transaction, transaction)
   
    
    else:
        return update_transaction_fields(db, db_transaction, transaction)    



def get_currency_from_transaction(db, username):
    transactions = db.query(Transaction.currency).filter(
        Transaction.username == username
    ).all()
    currency = [item.currency for item in transactions]
    currency = list(set(currency))
    return currency
    


def get_trade_v2(db, trade, username):
    '''
    최신 데이터 가져오기
    '''
    asset = crud_asset.get_asset_by_symbol(db, trade.code, username)
    print('trade', trade.__dict__)
    
    if trade.amount < 0:
        amount = abs(float(trade.amount)) + abs(float(trade.fee))
    else:
        amount = abs(float(trade.amount))
    if trade.price == None:
        trade.price = 0
    
    # trade.date를 datetime 형식으로 변환
    if isinstance(trade.date, str):
        trade_date = datetime.strptime(trade.date, '%Y-%m-%d')
    elif isinstance(trade.date, datetime):
        trade_date = trade.date
    else:  # date 객체인 경우
        trade_date = datetime.combine(trade.date, datetime.min.time())
    print('amount', amount)
    print(type(abs(float(trade.amount))), abs(float(trade.amount)))
    print(type(abs(float(trade.price))), abs(float(trade.price)))
    print(type(abs(float(trade.quantity))), abs(float(trade.quantity)))
    print(f"Converted trade_date: {trade_date}")  # 디버깅용
    
    result = db.query(Transaction).filter(
        Transaction.username == username,
        Transaction.date == trade_date,  # 변환된 date로 비교
        Transaction.amount.cast(Float) == amount,
        # Transaction.price.cast(Float) == abs(float(trade.price)),
        Transaction.quantity.cast(Float) == abs(float(trade.quantity)),
        Transaction.asset_id == asset.id
    ).first()
    print('result==============', result)
    return result

def get_old_trade_log(db: Session, db_old: Session, username: str):
    '''
    예전 데이터 가져오기
    '''
    transaction = {
        'date': '',
        'type': 'STOCK_BUY', # STOCK_BUY, STOCK_SELL, CRYPTO_BUY, CRYPTO_SELL
        'currency': '',
        'amount': 0,
        'note': '',
        'username': username,  # API에서 처리될 것임
        'debit_account_id': '',
        'credit_account_id': '',
        'fees': {},
        # SecurityTransactionCreate 추가 필드
        'asset_id': '',
        'quantity': 0,
        'price': 0,
        'exchange_rate': None,  # Optional
        'transaction_metadata': None  # Optional
    }
    fees_buy_krw = {
        '4101': {
            'amount': 0,
            'code': '4101',
            'currency': 'KRW',
            'id': 18,
            'name': '주식매매수수료'
        }        
    }
    fees_buy_usd = {
        '4101': {
            'amount': 0,
            'code': '4101',
            'currency': 'USD',
            'id': 18,
            'name': '주식매매수수료'
        }        
    }
    fees_krw_sell = {
        '4101': {
            'amount': 0,
            'code': '4101',
            'currency': 'KRW',
            'id': 18,
            'name': '주식매매수수료'
        },
        '4102': {
            'amount': 0,
            'code': '4102',
            'currency': 'KRW',
            'id': 19,
            'name': '증권거래세세'
        }
    }
    fees_usd_sell = {
        '4101': {
            'amount': 0,
            'code': '4101',
            'currency': 'USD',
            'id': 18,
            'name': '주식매매수수료'
        },
        '4004': {
            'amount': 0,
            'code': '4004',
            'currency': 'USD',
            'id': 23,
            'name': '인지세'
        }   
    }
    old_trade_log = get_all_old_trade_log(db_old, username)
    old_trade_log_list = sorted(old_trade_log, key=lambda x: x.date, reverse=False)
    for trade in old_trade_log_list:
        asset = crud_asset.get_asset_by_symbol(db, trade.code, username)
        if 'stock' in trade.asset_category and asset:
            # print(get_trade_v2(db, trade, username))
            # pprint(trade.__dict__)
            if 'dividend' in trade.asset_category:
                schema = schemas.IncomeTransactionCreate(
                    date=trade.date,
                    type='STOCK_INCOME',
                    asset_id=asset.id,
                    currency=asset.currency,
                    amount=trade.amount,
                    debit_account_id=41,
                    credit_account_id=26,
                    # note=trade.note,
                    fees={
                        '4107': {
                            'amount': abs(float(trade.tax)),
                            'code': '4107',
                            'currency': asset.currency,
                            'id': 43,
                            'name': '배당세'
                        }
                    },
                )
                print('dividend:', trade.__dict__)
                crud_income.db_create_income_transaction(db, schema, username)
            if trade.action == 'in' and 'dividend' not in trade.asset_category:
                # 최신 데이터가 있으면 넘어감
                if get_trade_v2(db, trade, username):
                    print('최신 데이터가 있으면 넘어감')
                    continue
                # Decimal을 float로 변환
                quantity = float(abs(trade.quantity))
                price = float(abs(trade.price))
                fee = float(abs(trade.fee))
                amount = quantity * price  # 이제 float 연산
                date = trade.date
                type = 'STOCK_BUY'
                currency = asset.currency
                asset_id = asset.id
                quantity = quantity
                price = price
                exchange_rate = None
                transaction_metadata = {}
                if currency == 'KRW':
                    debit_account_id = 39 # 주식 매입 계정 LS증권주식
                    credit_account_id = 38 # 주식 매입 계정 LS증권현금
                    if trade.fee:
                        fees_buy_krw['4101']['amount'] = float(abs(trade.fee))
                        fees = fees_buy_krw
                else:
                    debit_account_id = 42 # 주식 매입 계정 LS증권외환주식
                    credit_account_id = 41 # 주식 매입 계정 LS증권외환USD
                    if trade.fee:
                        fees_buy_usd['4101']['amount'] = float(abs(trade.fee))
                        fees = fees_buy_usd

                schema = schemas.SecurityTransactionCreate(
                    date=trade.date,
                    type=type,
                    asset_id=asset.id,
                    quantity=quantity,
                    price=price,
                    currency=currency,
                    amount=amount,
                    debit_account_id=debit_account_id,
                    credit_account_id=credit_account_id,
                    fees=fees,
                    # transaction_metadata=transaction_metadata,
                    username=username
                )
                print('schema==============')
                # pprint(schema.__dict__)
                crud_security_transaction.create_security_transaction_v2(db=db, transaction=schema, username=username)
            
            if trade.action == 'out' and 'dividend' not in trade.asset_category:
                if get_trade_v2(db, trade, username):
                    print('최신 데이터가 있으면 넘어감')
                    continue
                # Decimal을 float로 변환
                quantity = float(abs(trade.quantity))
                price = float(abs(trade.price))
                fee = float(abs(trade.fee))
                amount = quantity * price  # 이제 float 연산
                date = trade.date
                type = 'STOCK_SELL'
                currency = asset.currency
                asset_id = asset.id
                quantity = quantity
                price = price
                exchange_rate = None
                transaction_metadata = {}
                if currency == 'KRW':
                    debit_account_id = 38 # 주식 매입 계정 LS증권현금
                    credit_account_id = 39 # 주식 매입 계정 LS증권주식
                    if trade.fee:
                        fees_krw_sell['4101']['amount'] = float(abs(trade.fee))
                        fees_krw_sell['4102']['amount'] = float(abs(trade.tax))
                        fees = fees_krw_sell
                else:
                    debit_account_id = 41 # 주식 매입 계정 LS증권외환USD
                    credit_account_id = 42 # 주식 매입 계정 LS증권외환주식
                    if trade.fee:
                        fees_usd_sell['4101']['amount'] = float(abs(trade.fee))
                        fees_usd_sell['4004']['amount'] = float(abs(trade.tax))
                        fees = fees_usd_sell

                schema = schemas.SecurityTransactionCreate(
                    id=None,
                    date=trade.date,
                    type=type,
                    asset_id=asset.id,
                    quantity=quantity,
                    price=price,
                    currency=currency,
                    amount=amount,
                    debit_account_id=debit_account_id,
                    credit_account_id=credit_account_id,
                    fees=fees,
                    # transaction_metadata=transaction_metadata,
                    username=username
                )
                print('schema==============')
                pprint(schema.__dict__)
                crud_security_transaction.create_security_transaction_v2(db=db, transaction=schema, username=username)


def get_transactions_by_type(db_investment: Session, username: str, type: str):
    if type == 'asset':
        transactions = db_investment.query(Transaction).filter(
            Transaction.username == username,
        ).order_by(
            Transaction.date.desc(),
            Transaction.asset_id.asc()
        ).all()
    elif type == 'type':
        transactions = db_investment.query(Transaction).filter(
            Transaction.username == username,
        ).order_by(
            Transaction.date.desc(),
            Transaction.type.asc()
        ).all()
    elif type == 'date':
        transactions = db_investment.query(Transaction).filter(
            Transaction.username == username,
        ).order_by(
            Transaction.date.desc(),
            Transaction.asset_id.asc()
        ).all()
    return transactions

def recaculate_transaction(transactions, db_investment, username):
    try:
        for transaction in transactions:
            if transaction.type.endswith('SELL'):
                transaction.amount += transaction.transaction_metadata['profit_loss']
                transaction.price = transaction.amount / transaction.quantity
            elif transaction.type.endswith('BUY'):
                for _key, _value in transaction.fees.items():
                    transaction.amount -= _value['amount']
                transaction.price = transaction.amount / transaction.quantity
        return transactions
    except Exception as e:
        print('recaculate_transaction error:', e)
        return transactions

def get_transactions_all(
        key: str, 
        keyword: str,
        skip: int, 
        limit: int, 
        db_investment: Session, 
        db_stock: Session, 
        username: str
    ):
    # 기본 쿼리 생성 - asset 관계 포함
    base_query = db_investment.query(Transaction).options(
        joinedload(Transaction.asset)  # asset 관계 eager loading
    ).filter(
        Transaction.username == username
    )
    
    # # 정렬 조건 적용
    # if keyword == 'asset':
    #     base_query = base_query.order_by(
    #         Transaction.asset_id.asc(),
    #         Transaction.date.asc()
    #     )
    # elif keyword == 'type':
    #     base_query = base_query.order_by(
    #         Transaction.type.asc(),
    #         Transaction.date.asc()
    #     )
    # elif keyword == 'account':
    #     base_query = base_query.order_by(
    #         Transaction.debit_account_id.asc(),
    #         Transaction.date.asc()
    #     )
    # else:
    #     base_query = base_query.order_by(
    #         Transaction.date.asc()
    #     )
    
    # 전체 레코드 수 조회
    total_items = base_query.count()
    
    # 페이지네이션 적용
    # transactions = base_query.offset(skip).limit(limit).all()
    transactions = base_query.all()
    transactions = recaculate_transaction(transactions, db_investment, username)
    transactions = get_transactions_sort(transactions, db_investment, username)
    # 페이지네이션 정보 계산
    current_page = (skip // limit) + 1 if limit else 1
    total_pages = (total_items + limit - 1) // limit if limit else 1
    
    
    assetRealAmount = {}
    for currency, _value in transactions['active'].items():
        # print('transaction:', currency)
        # print('transaction:', _value)
        if currency not in assetRealAmount:
            assetRealAmount[currency] = 0
        for _key, _value in _value.items():
            for _key, _value in _value.items():
                if _key not in assetRealAmount:
                    if currency == 'USD':
                        price = get_fdr_price(db_stock, _key)[_key] 
                        quantity = _value['quantity']
                        amount = price * quantity
                    else:
                        price = 0
                        quantity = _value['quantity']
                        amount = 0
                    assetRealAmount[_key] = {
                        'currency': currency,
                        'exchange': _value['exchange'],
                        'amount': amount,
                        'quantity': quantity,
                        'price': price,
                    }

             
    pprint(assetRealAmount)    
            
    pagination = {
        "current_page": current_page,
        "items_per_page": limit,
        "total_items": total_items,
        "total_pages": total_pages
    } 
    
    return {
        "assetRealAmount": assetRealAmount,
        "items": transactions,
        "pagination": pagination
    }

    # # 디버깅용 출력 (필요시 사용)
    # for transaction in transactions:
    #     print('=='*100)
    #     for key, value in transaction.__dict__.items():
    #         print(f"{key}: {value}")

def get_transactions_sort(transactions, db_investment, username):
    '''
    자산별 거래 내역 정렬
    transactions_sort = {
        'active': {
            'currency': {
                'asset.currency': {
                    'asset.exchange': {
                        'asset.symbol': {
                            'name': asset.name,
                            'amount': 0,    
                            'quantity': 0,
                            'price': 0,
                            'fees': 0,
                            'pl': 0,
                            'transactions': []
                        }
                    }
                }
            }
        },
        'inactive': {
            'asset.currency': {
                'asset.exchange': {
                    'asset.symbol': {
                        'name': asset.name,
                        'fees': 0,
                        'pl': 0,
                            'transactions': []
                        }
                    }
                }
            }
        }
    }
    '''
    
    transactions_sort = {
        'active': {},
        'inactive': {}
    }
    
    for transaction in transactions:
        if transaction.asset_id:
            asset = crud_asset.get_asset_by_id(db_investment, transaction.asset_id, username)
            
            # currency 딕셔너리 초기화
            if asset.currency not in transactions_sort['active']:
                transactions_sort['active'][asset.currency] = {}
            if asset.currency not in transactions_sort['inactive']:
                transactions_sort['inactive'][asset.currency] = {}
                
            # exchange 딕셔너리 초기화
            if asset.exchange not in transactions_sort['active'][asset.currency]:
                transactions_sort['active'][asset.currency][asset.exchange] = {}
            if asset.exchange not in transactions_sort['inactive'][asset.currency]:
                transactions_sort['inactive'][asset.currency][asset.exchange] = {}
            
            # active/inactive 딕셔너리 초기화
            if asset.is_active and asset.symbol not in transactions_sort['active'][asset.currency][asset.exchange]:
                transactions_sort['active'][asset.currency][asset.exchange][asset.symbol] = {
                    'symbol': asset.symbol,
                    'exchange': asset.exchange,
                    'name': asset.name,
                    'amount': 0,
                    'quantity': 0,
                    'price': 0,
                    'fees': 0,
                    'pl': 0,
                    'transactions': []
                }
                
                 
            elif not asset.is_active and asset.symbol not in transactions_sort['inactive'][asset.currency][asset.exchange]:
                transactions_sort['inactive'][asset.currency][asset.exchange][asset.symbol] = {
                    'name': asset.name,
                    'fees': 0,
                    'pl': 0,
                    'transactions': []
                }
            
            # 거래 추가
            if asset.is_active:
                transactions_sort['active'][asset.currency][asset.exchange][asset.symbol]['transactions'].append(transaction)
                if transaction.type.endswith('BUY') and transaction.transaction_metadata['fifo']['quantity'] > 0:
                    # print(transaction.id, transaction.asset_id, transaction.date, transaction.type, transaction.transaction_metadata)
                    total_fees = get_total_fee(db_investment, transaction, username)
                    # print('total_fees:', total_fees)
                    quantity = transaction.transaction_metadata['fifo']['quantity']
                    price = (total_fees * quantity / transaction.quantity) / quantity + transaction.price
                    amount = quantity * price
                    transactions_sort['active'][asset.currency][asset.exchange][asset.symbol]['amount'] += amount
                    transactions_sort['active'][asset.currency][asset.exchange][asset.symbol]['quantity'] += quantity
                    transactions_sort['active'][asset.currency][asset.exchange][asset.symbol]['price'] = transactions_sort['active'][asset.currency][asset.exchange][asset.symbol]['amount'] / transactions_sort['active'][asset.currency][asset.exchange][asset.symbol]['quantity']
                if transaction.type.endswith('FEE'):
                    transactions_sort['active'][asset.currency][asset.exchange][asset.symbol]['fees'] += transaction.amount
                    # transactions_sort['active'][asset.currency][asset.exchange][asset.symbol]['pl'] -= transaction.amount
                if transaction.type.endswith('PROFIT'):
                    transactions_sort['active'][asset.currency][asset.exchange][asset.symbol]['pl'] += transaction.amount
                if transaction.type.endswith('LOSS'):
                    transactions_sort['active'][asset.currency][asset.exchange][asset.symbol]['pl'] -= transaction.amount
                    
                 
                
            else:
                transactions_sort['inactive'][asset.currency][asset.exchange][asset.symbol]['transactions'].append(transaction)
                if transaction.type.endswith('FEE'):
                    transactions_sort['inactive'][asset.currency][asset.exchange][asset.symbol]['fees'] += transaction.amount
                if transaction.type.endswith('INCOME') or transaction.type.endswith('PROFIT'):
                    transactions_sort['inactive'][asset.currency][asset.exchange][asset.symbol]['pl'] += transaction.amount
                if transaction.type.endswith('LOSS'):
                    transactions_sort['inactive'][asset.currency][asset.exchange][asset.symbol]['pl'] -= transaction.amount
        else:
            if transaction.type not in transactions_sort:
                transactions_sort[transaction.type] = []
            transactions_sort[transaction.type].append(transaction)
    
    # pprint(transactions_sort)
    # print('='*100)
    
    return transactions_sort



def get_transactions_all_db(db_investment, username):
    base_query = db_investment.query(Transaction).filter(
        Transaction.username == username
    ).all()
    return base_query



# 월별 수익율
def calculate_periodic_returns(db_investment, username, period='monthly'):
    """월별/연도별 수익률 계산"""
    transactions = get_transactions_all_db(db_investment, username)
    returns = {}
    
    for transaction in transactions:
        if transaction.type.endswith(('PROFIT', 'LOSS', 'INCOME')):
            date = transaction.date
            year = date.year
            month = date.month if period == 'monthly' else None
            
            # 키 생성
            _key = f"{year}-{month:02d}" if period == 'monthly' else str(year)
            
            if _key not in returns:
                returns[_key] = {
                    'profit': 0,
                    'loss': 0,
                    'income': 0,
                    'total': 0
                }
            
            amount = transaction.amount
            if transaction.type.endswith('PROFIT'):
                returns[_key]['profit'] += amount
            elif transaction.type.endswith('LOSS'):
                returns[_key]['loss'] += amount
            elif transaction.type.endswith('INCOME'):
                returns[_key]['income'] += amount
                
            returns[_key]['total'] = (
                returns[_key]['profit'] + 
                returns[_key]['income'] - 
                returns[_key]['loss']
            )
    
    # 정렬된 결과 반환
    sorted_returns = dict(sorted(returns.items()))
    return sorted_returns




def get_last_price(key, db_investment, db_stock, username):
    assets = crud_asset.get_asset_is_active(db_investment, username)
    codes = ''
    symbols = []
    price_dict = {}
    for asset in assets:
        if asset.exchange in ['KOSPI', 'KOSDAQ']:
            codes += asset.symbol
        elif asset.currency == 'USD' and asset.type.lower() == 'stock':
            symbols.append(asset.symbol)
    if symbols:
        fdr_datas = get_fdr_price(db_stock, ','.join(symbols))
    if codes:
        multi_t8407 = get_multi_t8407(key, username, db_stock, codes)
    
    for key, value in fdr_datas.items():
        price_dict[key] = value
    for t8407 in multi_t8407:
        price_dict[t8407['종목코드']] = t8407['현재가']
    
    return price_dict

def get_asset_summary(
        key: str,
        date: str,
        db_investment: Session, 
        db_stock: Session, 
        username: str
    ):    
    # SQLite용 연도 추출 쿼리
    years = db_investment.query(
        func.strftime('%Y', Transaction.date).label('year')
    ).filter(
        Transaction.username == username
    ).distinct().order_by(
        func.strftime('%Y', Transaction.date).desc()
    ).all()
    
    years = [int(year[0]) for year in years if year[0]]
    
    # 현재 사용할 연도 결정
    current_year = datetime.now().year
    try:
        if date and date not in ['asset', 'type', 'account', 'date']:
            selected_year = int(date)
        else:
            selected_year = current_year
    except ValueError:
        selected_year = current_year

    # 기존 쿼리 로직...
    query = db_investment.query(Transaction).join(
        Transaction.asset
    ).filter(
        Transaction.username == username,
        extract('year', Transaction.date) == selected_year
    )
    
    # 쿼리 실행
    transactions = query.order_by(Transaction.date.desc()).all()

    fifo_dict = {}
    for transaction in transactions:
        if transaction.asset_id:
            asset_name = transaction.asset.name
            code = transaction.asset.symbol
            
            if ('SELL' in transaction.type.upper() and 
                transaction.transaction_metadata and 
                'summary' in transaction.transaction_metadata):
                
                if transaction.currency not in fifo_dict:
                    fifo_dict[transaction.currency] = {
                        'total_pl': 0,
                        'list': []
                    }   
                
                for fifo in transaction.transaction_metadata['summary']:
                    fifo_dict[transaction.currency]['total_pl'] += fifo['realized_pl']
                    fifo['currency'] = transaction.currency
                    fifo['asset_name'] = asset_name
                    fifo['code'] = code
                    fifo['date'] = transaction.date.strftime('%Y-%m-%d')  # 날짜 정보 추가
                    fifo_dict[transaction.currency]['list'].append(fifo)
    
    
    # 연도 정보 추가
    fifo_dict['years'] = years
    fifo_dict['selected_year'] = selected_year
    
    return fifo_dict

def get_transaction_summary(db: Session, username: str):
    """거래 내역 요약"""
    summary = db.query(
        Transaction.asset_id,
        Transaction.currency,
        func.sum(case(
            (Transaction.type.like('%BUY%'), Transaction.quantity),
            else_=0
        )).label('total_buy_quantity'),
        func.sum(case(
            (Transaction.type.like('%SELL%'), Transaction.quantity),
            else_=0
        )).label('total_sell_quantity'),
        func.sum(case(
            (Transaction.type.like('%BUY%'), Transaction.amount),
            else_=0
        )).label('total_purchase_amount'),
        func.sum(case(
            (Transaction.type.like('%SELL%'), Transaction.amount),
            else_=0
        )).label('total_sell_amount'),
        # 평균 매수가 계산
        (func.sum(case(
            (Transaction.type.like('%BUY%'), Transaction.amount),
            else_=0
        )) / func.nullif(func.sum(case(
            (Transaction.type.like('%BUY%'), Transaction.quantity),
            else_=0
        )), 0)).label('average_price'),
    ).filter(
        Transaction.username == username
    ).group_by(
        Transaction.asset_id,
        Transaction.currency
    ).all()

    return [{
        'asset_id': item.asset_id,
        'currency': item.currency,
        'total_buy_quantity': float(item.total_buy_quantity),
        'total_sell_quantity': float(item.total_sell_quantity),
        'remaining_quantity': float(item.total_buy_quantity - item.total_sell_quantity),
        'total_purchase_amount': float(item.total_purchase_amount),
        'total_sell_amount': float(item.total_sell_amount),
        'average_price': float(item.average_price) if item.average_price else 0,
        'realized_pl': float(item.total_sell_amount - 
            (item.total_sell_quantity * item.average_price if item.average_price else 0))
    } for item in summary]




def analyze_transactions_by_currency(db: Session, username: str, exchange_rates: dict = None):
    """통화별 차변/대변 분석"""
    
    exchange_rates = crud_exchange.get_latest_rates(db, username)
    pprint(exchange_rates)
    
    # 1. 통화별 원본 데이터
    balances_by_currency = {}
    
    currencies = get_currency_from_transaction(db, username)
    
    for currency in currencies:
        account_balances = db.query(
            Account.id,
            Account.name,
            Account.category,
            Account.code,
            func.sum(case(
                # 일반 거래의 차변 (환전 제외)
                (and_(
                    Transaction.debit_account_id == Account.id,
                    Transaction.currency == currency,
                    Transaction.type != 'EXCHANGE'
                ), Transaction.amount),
                else_=0
            )).label('debit_total'),
            func.sum(case(
                # 일반 거래의 대변 (환전 제외)
                (and_(
                    Transaction.credit_account_id == Account.id,
                    Transaction.currency == currency,
                    Transaction.type != 'EXCHANGE'
                ), Transaction.amount),
                else_=0
            )).label('credit_total'),
            # 환전 거래 별도 계산
            # func.sum(case(
            #     (and_(
            #         Transaction.type == 'EXCHANGE',
            #         Transaction.currency == currency,
            #         Transaction.debit_account_id == Account.id
            #     ), Transaction.amount),
            #     else_=0
            # )).label('exchange_debit'),
            # func.sum(case(
            #     (and_(
            #         Transaction.type == 'EXCHANGE',
            #         Transaction.currency == currency,
            #         Transaction.credit_account_id == Account.id
            #     ), Transaction.amount),
            #     else_=0
            # )).label('exchange_credit')
        ).join(
            Transaction,
            or_(
                Transaction.debit_account_id == Account.id,
                Transaction.credit_account_id == Account.id
            )
        ).filter(
            Transaction.username == username
        ).group_by(
            Account.id,
            Account.name,
            Account.category,
            Account.code
        ).all()

        # 각 통화별 계정 데이터 및 요약 계산
        accounts_list = []
        summary = {
            "assets": 0,
            "liabilities": 0,
            "equity": 0,
            "revenue": 0,    # 수익 추가
            "expense": 0,    # 비용 추가
            "exchange_net": 0
        }

        for acc in account_balances:
            # 일반 거래 잔액
            regular_balance = float(acc.debit_total - acc.credit_total) \
                if acc.code and acc.code.startswith(('1', '4')) \
                else float(acc.credit_total - acc.debit_total)
            
            # # 환전 거래 잔액
            # exchange_balance = float(acc.exchange_debit - acc.exchange_credit) \
            #     if acc.code and acc.code.startswith(('1', '4')) \
            #     else float(acc.exchange_credit - acc.exchange_debit)

            # 최종 잔액
            total_balance = regular_balance
                
            account_data = {
                "id": acc.id,
                "name": acc.name,
                "category": acc.category,
                "code": acc.code,
                "debit_total": float(acc.debit_total),
                "credit_total": float(acc.credit_total),
                "balance": total_balance
            }
            accounts_list.append(account_data)
            
            # summary 업데이트 - 계정 코드에 따라 분류
            if acc.code.startswith('1'):        # 자산
                summary["assets"] += total_balance
            elif acc.code.startswith('2'):      # 부채
                summary["liabilities"] += total_balance
            elif acc.code.startswith('3'):      # 자본
                summary["equity"] += total_balance
            elif acc.code.startswith('4'):      # 비용
                summary["expense"] += total_balance
            elif acc.code.startswith('5'):      # 수익
                summary["revenue"] += total_balance

        # 순자산 = 자산 - 부채
        summary["net_assets"] = summary["assets"] - summary["liabilities"]
        # 순이익 = 수익 - 비용
        summary["net_income"] = summary["revenue"] - summary["expense"]
        # 자본 조정 (순이익 반영)
        summary["equity"] += summary["net_income"]
        
        balances_by_currency[currency] = {
            "accounts": accounts_list,
            "summary": summary
        }

    # validations 수정
    validations = {
        currency: {
            "assets_equal_liabilities_and_equity": 
                abs(data["summary"]["assets"] - 
                    (data["summary"]["liabilities"] + 
                     data["summary"]["equity"])) < 0.01,
            "net_income_reflected": 
                abs(data["summary"]["net_income"] - 
                    (data["summary"]["revenue"] - 
                     data["summary"]["expense"])) < 0.01
        }
        for currency, data in balances_by_currency.items()
    }

        
    # pprint(balances_by_currency)
    
    # 원화 환산 총액 계산 추가
    total_assets_krw = calculate_total_assets_in_krw(balances_by_currency, exchange_rates)
    # pprint({
    #     "by_currency": balances_by_currency,  # 통화별 원본 데이터
    #     "total_assets_krw": total_assets_krw,
    #     "validations": {
    #         currency: {
    #             "assets_equal_liabilities_and_equity": 
    #                 abs(data["summary"]["assets"] - 
    #                     (data["summary"]["liabilities"] + 
    #                      data["summary"]["equity"])) < 0.01
    #         }
    #         for currency, data in balances_by_currency.items()
    #     }
    # })
    
    
    return {
        "by_currency": balances_by_currency,  # 통화별 원본 데이터
        "total_assets_krw": total_assets_krw,
        "validations": {
            currency: {
                "assets_equal_liabilities_and_equity": 
                    abs(data["summary"]["assets"] - 
                        (data["summary"]["liabilities"] + 
                         data["summary"]["equity"])) < 0.01
            }
            for currency, data in balances_by_currency.items()
        }
    }

    

def calculate_total_assets_in_krw(balances_by_currency: dict, exchange_rates: dict) -> dict:
    """각 통화별 자산을 원화로 환산하여 총 자산 계산"""
    total_in_krw = {
        'total': 0,
        'by_currency': {}
    }
    
    for currency, data in balances_by_currency.items():
        if currency == 'KRW':
            # KRW는 그대로 사용
            amount_in_krw = data['summary']['assets']
        else:
            # 다른 통화는 환율을 적용하여 KRW로 변환
            exchange_rate = exchange_rates.get(currency, {}).get('KRW', {}).get('rate')
            if exchange_rate:
                amount_in_krw = data['summary']['assets'] * exchange_rate
            else:
                print(f"Warning: No exchange rate found for {currency}/KRW")
                amount_in_krw = 0
        
        total_in_krw['by_currency'][currency] = {
            'original': data['summary']['assets'],
            'in_krw': amount_in_krw
        }
        total_in_krw['total'] += amount_in_krw
    
    return total_in_krw
    
    
    
    
    


def get_transaction_by_asset_id(db: Session, asset_id: int, username: str):
    """자산별 거래 내역 조회"""
    return db.query(Transaction).filter(
        Transaction.asset_id == asset_id,
        Transaction.username == username
    ).all()


def get_asset_account_summary(db: Session, asset_id: int, username: str):
    """자산별 차변/대변 계정 요약"""
    
    transactions = db.query(Transaction).options(
        joinedload(Transaction.debit_account),
        joinedload(Transaction.credit_account)
    ).filter(
        Transaction.asset_id == asset_id,
        Transaction.username == username
    ).all()
    
    summary = {
        'debit_accounts': {  # 자산, 비용 계정
            'accounts': {},
            'total': 0
        },
        'credit_accounts': {  # 자본, 수익, 부채 계정
            'accounts': {},
            'total': 0
        }
    }
    
    for tx in transactions:
        # 차변 계정 처리
        debit_code = tx.debit_account.code
        debit_name = tx.debit_account.name
        
        # 자산(1), 비용(4) 계정
        if debit_code.startswith(('1', '4')):
            if debit_name not in summary['debit_accounts']['accounts']:
                summary['debit_accounts']['accounts'][debit_name] = {
                    'total': 0,
                    'code': debit_code,
                    'transactions': []
                }
            summary['debit_accounts']['accounts'][debit_name]['total'] += tx.amount
            summary['debit_accounts']['total'] += tx.amount
            summary['debit_accounts']['accounts'][debit_name]['transactions'].append({
                'date': tx.date,
                'type': tx.type,
                'amount': tx.amount
            })
        
        # 대변 계정 처리
        credit_code = tx.credit_account.code
        credit_name = tx.credit_account.name
        
        # 자본, 수익, 부채(2,3,5) 계정
        if credit_code.startswith(('2', '3', '5')):
            if credit_name not in summary['credit_accounts']['accounts']:
                summary['credit_accounts']['accounts'][credit_name] = {
                    'total': 0,
                    'code': credit_code,
                    'transactions': []
                }
            summary['credit_accounts']['accounts'][credit_name]['total'] += tx.amount
            summary['credit_accounts']['total'] += tx.amount
            summary['credit_accounts']['accounts'][credit_name]['transactions'].append({
                'date': tx.date,
                'type': tx.type,
                'amount': tx.amount
            })
    
    return summary


def get_asset_profit_loss(db: Session, asset_id: int, username: str):
    """자산별 손익 계산"""
    
    # 거래 내역 조회
    transactions = db.query(Transaction).filter(
        Transaction.asset_id == asset_id,
        Transaction.username == username
    ).all()
    
    profit_loss = {
        'buy_amount': 0,
        'sell_amount': 0,
        'income': 0,
        'income_detail': {},
        'expense': 0,
        'expense_detail': {},
        'cost': 0,
        'cost_detail': {},
        'profit': 0,
        'profit_rate': 0,
    }
    
    for tx in transactions:
        # 매수/매도 금액
        if 'BUY' in tx.type.upper():
            profit_loss['buy_amount'] += tx.amount
            
        elif 'SELL' in tx.type.upper():
            profit_loss['sell_amount'] += tx.amount
            if tx.transaction_metadata and 'bought_amount' in tx.transaction_metadata:
                profit_loss['buy_amount'] += tx.transaction_metadata['bought_amount']
                
        # 수수료/비용
        if tx.fees:
            for fee in tx.fees.values():
                fee_name = fee['name']
                fee_amount = fee['amount']
                profit_loss['cost'] += fee_amount
                if fee_name not in profit_loss['cost_detail']:
                    profit_loss['cost_detail'][fee_name] = fee_amount
                else:
                    profit_loss['cost_detail'][fee_name] += fee_amount
                    
        # 수익/비용
        if 'INCOME' in tx.type.upper():
            profit_loss['income'] += tx.amount
            income_name = tx.credit_account.name
            if income_name not in profit_loss['income_detail']:
                profit_loss['income_detail'][income_name] = tx.amount
            else:
                profit_loss['income_detail'][income_name] += tx.amount
                
        elif 'EXPENSE' in tx.type.upper():
            profit_loss['expense'] += tx.amount
            expense_name = tx.debit_account.name
            if expense_name not in profit_loss['expense_detail']:
                profit_loss['expense_detail'][expense_name] = tx.amount
            else:
                profit_loss['expense_detail'][expense_name] += tx.amount
    
    # 손익 및 수익률 계산
    total_profit = (profit_loss['sell_amount'] - profit_loss['buy_amount'] - 
                   profit_loss['cost'] + profit_loss['income'] - profit_loss['expense'])
    profit_loss['profit'] = total_profit
    
    if profit_loss['buy_amount'] > 0:
        profit_loss['profit_rate'] = total_profit / profit_loss['buy_amount']
    
    return profit_loss



























def calculate_periodic_returns_v2(db: Session, username: str):
    # """월별/연도별 수익률 계산"""
    transactions = get_transactions_all_db(db, username)
    # print('transactions:', transactions)
    date_list = []
    for tx in transactions:
        # day는 생략
        date_list.append(tx.date.strftime('%Y-%m'))
    date_list = list(set(date_list))
    date_list.sort()
    currencies = crud_exchange.get_currencies(db, username)
    accounts = crud_account.get_accounts_by_transaction(db, username)
    assets = crud_asset.get_account_assets_symbol_by_transaction(db, username)
    # pprint(assets)
    
    
    # 손익 계산서
    income_statement = {}
    for date in date_list:
        income_statement[date] = {}
        for currency in currencies:
            income_statement[date][currency] = {
                'revenues': {
                    'total': 0,
                    'sales': {
                        'total': 0,
                    },
                    'valuation': {
                        'total': 0,
                    }
                },
                'expenses': {
                    'total': 0,
                },
                'net_income': 0
            }
            for account in accounts:
                if account.code.startswith('5'):
                    income_statement[date][currency]['revenues'][account.name] = {
                        'total': 0,
                    }
            for account in accounts:
                if account.code.startswith('4'):
                    income_statement[date][currency]['expenses'][account.name] = {
                        'total': 0,
                    }
                    
            for asset_currency in assets:
                if asset_currency == currency:
                    for account_name in assets[asset_currency]:
                        income_statement[date][asset_currency]['revenues']['sales'][account_name] = {}
                        income_statement[date][asset_currency]['revenues']['valuation'][account_name] = {}
                        # for symbol in assets[asset_currency][account_name]:
                        #     income_statement[date][asset_currency]['revenues']['sales'][account_name][symbol] = 0
                        #     income_statement[date][asset_currency]['revenues']['valuation'][account_name][symbol] = 0
    
    
    # 재무제표 초기화
    balance = {}
    for date in date_list:  
        balance[date] = {}
        for currency in currencies:
            balance[date][currency] = {
                'assets': {
                    'total': 0,
                },        # 자산
                'liabilities': {
                    'total': 0,
                },   # 부채
                'equity': {
                    'total': 0,
                },        # 자본
                'revenues': {
                    'total': 0,
                },      # 수익
                'expenses': {
                    'total': 0,
                },      # 비용
                'holdings': {
                    'total': 0,
                }       # 보유현황
            }
            for account in accounts:
                if account.code.startswith('1'):
                    balance[date][currency]['assets'][account.name] = 0
                elif account.code.startswith('2'):
                    balance[date][currency]['liabilities'][account.name] = 0
                elif account.code.startswith('3'):
                    balance[date][currency]['equity'][account.name] = 0
                elif account.code.startswith('4'):
                    balance[date][currency]['expenses'][account.name] = 0
                elif account.code.startswith('5'):
                    balance[date][currency]['revenues'][account.name] = 0
                for asset_currency in assets:
                    if asset_currency == currency:
                        for account_name in assets[asset_currency]:
                            balance[date][asset_currency]['holdings'][account_name] = {}
                            for symbol in assets[asset_currency][account_name]:
                                balance[date][asset_currency]['holdings'][account_name][symbol] = 0
                    
    # pprint(balance)
    
    # 재무제표 업데이트
    for i, date in enumerate(date_list):
        print('date:', date)
        transactions_by_date = [tx for tx in transactions if tx.date.strftime('%Y-%m') == date and tx.type != 'EXCHANGE']
        if i > 0:
            for currency in balance[date_list[i-1]]:
                for account in balance[date_list[i-1]][currency]:
                    if account != 'holdings':
                        balance[date][currency][account] = balance[date_list[i-1]][currency][account].copy()
            
            
            for asset_currency in assets:
                for account_name in assets[asset_currency]:
                    for symbol in assets[asset_currency][account_name]:
                        if balance[date][asset_currency]['holdings'][account_name][symbol] == 0:
                                balance[date][asset_currency]['holdings'][account_name][symbol] = balance[date_list[i-1]][asset_currency]['holdings'][account_name][symbol]
        
        # 거래 내역 업데이트
        for tx in transactions_by_date:
            
            if tx.type.upper().endswith('SELL'):
                income_statement[date][tx.currency]['revenues']['sales']['total'] += tx.amount
                if tx.asset.name not in income_statement[date][tx.currency]['revenues']['sales'][tx.credit_account.name]:
                    income_statement[date][tx.currency]['revenues']['sales'][tx.credit_account.name][tx.asset.name] = 0
                income_statement[date][tx.currency]['revenues']['sales'][tx.credit_account.name][tx.asset.name] += tx.amount
            
            
            if tx.debit_account.code.startswith('1'):       # 자산
                balance[date][tx.currency]['assets'][tx.debit_account.name] += tx.amount
                balance[date][tx.currency]['assets']['total'] += tx.amount
            elif tx.debit_account.code.startswith('2'):    # 부채
                balance[date][tx.currency]['liabilities'][tx.debit_account.name] -= tx.amount
                balance[date][tx.currency]['liabilities']['total'] -= tx.amount
            elif tx.debit_account.code.startswith('3'):    # 자본
                balance[date][tx.currency]['equity'][tx.debit_account.name] -= tx.amount
                balance[date][tx.currency]['equity']['total'] -= tx.amount
            elif tx.debit_account.code.startswith('4'):    # 비용
                balance[date][tx.currency]['expenses'][tx.debit_account.name] += tx.amount
                balance[date][tx.currency]['expenses']['total'] += tx.amount
                
                # 손익계산서 업데이트
                if tx.debit_account.code == '4301':
                    income_statement[date][tx.currency]['net_income'] -= tx.amount
                    income_statement[date][tx.currency]['expenses']['total'] += tx.amount
                    income_statement[date][tx.currency]['expenses'][tx.debit_account.name]['total'] += tx.amount
                    print('tx.asset.symbol:', tx.asset.symbol)
                    if tx.asset.name not in income_statement[date][tx.currency]['expenses'][tx.debit_account.name]:
                        income_statement[date][tx.currency]['expenses'][tx.debit_account.name][tx.asset.name] = 0
                    income_statement[date][tx.currency]['expenses'][tx.debit_account.name][tx.asset.name] += tx.amount
                else:
                    income_statement[date][tx.currency]['net_income'] -= tx.amount
                    income_statement[date][tx.currency]['expenses']['total'] += tx.amount
                    income_statement[date][tx.currency]['expenses'][tx.debit_account.name]['total'] += tx.amount
                
                
                
            elif tx.debit_account.code.startswith('5'):    # 수익
                balance[date][tx.currency]['revenues'][tx.debit_account.name] -= tx.amount
                balance[date][tx.currency]['revenues']['total'] -= tx.amount
            if tx.credit_account.code.startswith('1'):      # 자산
                balance[date][tx.currency]['assets'][tx.credit_account.name] -= tx.amount
                balance[date][tx.currency]['assets']['total'] -= tx.amount
            elif tx.credit_account.code.startswith('2'):    # 부채
                balance[date][tx.currency]['liabilities'][tx.credit_account.name] += tx.amount
                balance[date][tx.currency]['liabilities']['total'] += tx.amount
            elif tx.credit_account.code.startswith('3'):    # 자본
                balance[date][tx.currency]['equity'][tx.credit_account.name] += tx.amount
                balance[date][tx.currency]['equity']['total'] += tx.amount
            elif tx.credit_account.code.startswith('4'):    # 비용
                balance[date][tx.currency]['expenses'][tx.credit_account.name] -= tx.amount
                balance[date][tx.currency]['expenses']['total'] -= tx.amount
            elif tx.credit_account.code.startswith('5'):    # 수익
                balance[date][tx.currency]['revenues'][tx.credit_account.name] += tx.amount
                balance[date][tx.currency]['revenues']['total'] += tx.amount
                
                # 손익계산서 업데이트
                if tx.credit_account.code == '5301':
                    print('tx.asset.symbol:', tx.date, tx.asset.name, tx.amount)
                    income_statement[date][tx.currency]['net_income'] += tx.amount
                    income_statement[date][tx.currency]['revenues']['total'] += tx.amount
                    income_statement[date][tx.currency]['revenues'][tx.credit_account.name]['total'] += tx.amount
                    print('tx.asset.symbol:', tx.asset.symbol)
                    if tx.asset.name not in income_statement[date][tx.currency]['revenues'][tx.credit_account.name]:
                        income_statement[date][tx.currency]['revenues'][tx.credit_account.name][tx.asset.name] = 0
                    income_statement[date][tx.currency]['revenues'][tx.credit_account.name][tx.asset.name] += tx.amount
                else:
                    income_statement[date][tx.currency]['net_income'] += tx.amount
                    income_statement[date][tx.currency]['revenues']['total'] += tx.amount
                    income_statement[date][tx.currency]['revenues'][tx.credit_account.name]['total'] += tx.amount
            
            
            if tx.asset_id:
                if not tx.quantity:
                    continue
                symbol = tx.asset.symbol
                if tx.type.upper().endswith('BUY'): 
                    balance[date][tx.currency]['holdings'][tx.debit_account.name][symbol] += tx.quantity
                else:
                    balance[date][tx.currency]['holdings'][tx.credit_account.name][symbol] -= tx.quantity
                
    # pprint(balance)
    # print('=============='*5)
    # 평가차손/평가차익 계산
    for i, date in enumerate(date_list):
        for currency in balance[date]:
            for account in balance[date][currency]:
                if account != 'holdings':
                    pass
                else:
                    average_amount = (balance[date][currency]['assets']['total'] + balance[date_list[i-1]][currency]['assets']['total'])/2
                    print('average_amount:', average_amount)
                    income_statement[date][currency]['revenues']['sales']['turnover_rate'] = 100 * income_statement[date][currency]['revenues']['sales']['total'] / average_amount
                    for account_name in balance[date][currency]['holdings']:
                        total_amount = 0
                        if account_name == 'total':
                            continue
                        for symbol_key, symbol_value in balance[date][currency]['holdings'][account_name].items():
                            year, month = date.split('-')
                            last_day = monthrange(int(year), int(month))[1]
                            fdr_date = year + '-' + month + '-' + str(last_day)
                            if datetime.strptime(fdr_date, '%Y-%m-%d') > datetime.now():
                                fdr_date = datetime.now().strftime('%Y-%m-%d')
                            fdr_price = get_fdr_price(db, symbol_key, fdr_date)[symbol_key]
                            total_amount += fdr_price * symbol_value
                        balance[date][currency]['assets'][account_name + 'II'] = total_amount
                        balance[date][currency]['assets']['total'] += total_amount - balance[date][currency]['assets'][account_name]
                        pl = total_amount - balance[date][currency]['assets'][account_name]
                        print('pl:', pl)
                        
                        if pl < 0:
                            balance[date][currency]['expenses']['평가차손'] = abs(pl)
                            
                            income_statement[date][currency]['net_income'] -= abs(pl)
                            income_statement[date][currency]['expenses']['total'] += abs(pl)
                            if '평가차손' not in income_statement[date][currency]['expenses']:
                                income_statement[date][currency]['expenses']['평가차손'] = 0
                            income_statement[date][currency]['expenses']['평가차손'] += abs(pl)
                        
                        else:
                            balance[date][currency]['revenues']['평가차익'] = abs(pl)
                        
                        
                            income_statement[date][currency]['net_income'] += abs(pl)
                            income_statement[date][currency]['revenues']['total'] += abs(pl)
                            if '평가차익' not in income_statement[date][currency]['revenues']:
                                income_statement[date][currency]['revenues']['평가차익'] = 0
                            income_statement[date][currency]['revenues']['평가차익'] += abs(pl)
                        
    
    
    print('=============='*5)
    pprint(income_statement)
                    
    print('=============='*5)
    pprint(balance)
    
    return {
        'balance': balance,
        'income_statement': income_statement
    }
    
    
    

def get_monthly_financial_statements(db: Session, username: str):
    """월별 재무상태표와 손익계산서 생성"""
    transactions = get_transactions_all_db(db, username)
    
    # 날짜 목록 생성 및 정렬
    date_list = list(set(tx.date.strftime('%Y-%m') for tx in transactions))
    date_list.sort()
    
    # 재무제표 저장용 딕셔너리
    financial_statements = {}
    cumulative_balance = {}  # 누적 잔액
    
    for date in date_list:
        year, month = date.split('-')
        last_day = monthrange(int(year), int(month))[1]
        statement_date = f"{year}-{month}-{last_day}"
        
        if datetime.strptime(statement_date, '%Y-%m-%d') > datetime.now():
            statement_date = datetime.now().strftime('%Y-%m-%d')
        
        financial_statements[date] = {
            'balance_sheet': {
                'assets': {'total': 0},          # 자산
                'liabilities': {'total': 0},     # 부채
                'equity': {'total': 0}           # 자본
            },
            'income_statement': {
                'revenues': {'total': 0},        # 수익
                'expenses': {'total': 0},        # 비용
                'net_income': 0                  # 당기순이익
            }
        }
        
        # 이전 월의 잔액 이월
        if len(cumulative_balance) > 0:
            for account, balance in cumulative_balance.items():
                category = get_account_category(account)
                if category in ['assets', 'liabilities', 'equity']:
                    financial_statements[date]['balance_sheet'][category][account] = balance
                    financial_statements[date]['balance_sheet'][category]['total'] += balance
        
        # 당월 거래 처리
        monthly_transactions = [tx for tx in transactions if tx.date.strftime('%Y-%m') == date]
        for tx in monthly_transactions:
            # 차변 계정 처리
            debit_category = get_account_category(tx.debit_account.code)
            if debit_category in ['assets', 'expenses']:
                amount = tx.amount
            else:
                amount = -tx.amount
                
            update_financial_statement(
                financial_statements[date],
                debit_category,
                tx.debit_account.name,
                amount,
                tx
            )
            
            # 대변 계정 처리
            credit_category = get_account_category(tx.credit_account.code)
            if credit_category in ['liabilities', 'equity', 'revenues']:
                amount = tx.amount
            else:
                amount = -tx.amount
                
            update_financial_statement(
                financial_statements[date],
                credit_category,
                tx.credit_account.name,
                amount,
                tx
            )
            
            # 자산 평가금액 업데이트
            if tx.asset_id and tx.type != 'EXCHANGE':
                symbol = tx.asset.symbol
                fdr_price = get_fdr_price(db, symbol, statement_date)[symbol]
                
                if tx.type.endswith('BUY'):
                    quantity = tx.quantity if tx.quantity is not None else 0
                    financial_statements[date]['balance_sheet']['assets'][f'{symbol}_shares'] = \
                        financial_statements[date]['balance_sheet']['assets'].get(f'{symbol}_shares', 0) + quantity
                    financial_statements[date]['balance_sheet']['assets'][f'{symbol}_value'] = \
                        financial_statements[date]['balance_sheet']['assets'][f'{symbol}_shares'] * fdr_price
                elif tx.type.endswith('SELL'):
                    quantity = tx.quantity if tx.quantity is not None else 0
                    financial_statements[date]['balance_sheet']['assets'][f'{symbol}_shares'] = \
                        financial_statements[date]['balance_sheet']['assets'].get(f'{symbol}_shares', 0) - quantity
                    financial_statements[date]['balance_sheet']['assets'][f'{symbol}_value'] = \
                        financial_statements[date]['balance_sheet']['assets'][f'{symbol}_shares'] * fdr_price
        
        # 당기순이익 계산
        net_income = (financial_statements[date]['income_statement']['revenues']['total'] - 
                     financial_statements[date]['income_statement']['expenses']['total'])
        financial_statements[date]['income_statement']['net_income'] = net_income
        
        # 자본 총계에 당기순이익 반영
        financial_statements[date]['balance_sheet']['equity']['retained_earnings'] = \
            financial_statements[date]['balance_sheet']['equity'].get('retained_earnings', 0) + net_income
        financial_statements[date]['balance_sheet']['equity']['total'] += net_income
        
        # 누적 잔액 업데이트
        update_cumulative_balance(cumulative_balance, financial_statements[date])
    
    return financial_statements

def get_account_category(account_code: str) -> str:
    """계정 코드로 카테고리 반환"""
    if account_code.startswith('1'):
        return 'assets'
    elif account_code.startswith('2'):
        return 'liabilities'
    elif account_code.startswith('3'):
        return 'equity'
    elif account_code.startswith('4'):
        return 'expenses'
    elif account_code.startswith('5'):
        return 'revenues'
    return 'unknown'

def update_financial_statement(statement: dict, category: str, account_name: str, amount: float, tx: Transaction):
    """재무제표 업데이트"""
    if category in ['assets', 'liabilities', 'equity']:
        statement['balance_sheet'][category][account_name] = \
            statement['balance_sheet'][category].get(account_name, 0) + amount
        statement['balance_sheet'][category]['total'] += amount
    elif category in ['revenues', 'expenses']:
        statement['income_statement'][category][account_name] = \
            statement['income_statement'][category].get(account_name, 0) + amount
        statement['income_statement'][category]['total'] += amount

def update_cumulative_balance(cumulative: dict, statement: dict):
    """누적 잔액 업데이트"""
    for category in ['assets', 'liabilities', 'equity']:
        for account, balance in statement['balance_sheet'][category].items():
            if account != 'total':
                cumulative[account] = balance



