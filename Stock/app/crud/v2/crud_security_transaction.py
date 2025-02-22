from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import func, and_, cast, Float, JSON, text
from datetime import datetime
from typing import List, Optional, Dict, Any

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


from pprint import pprint


def create_or_update_sell_transaction(db, transaction, asset_type, transaction_metadata, username):
    print('transaction----------------------------------------------------:', transaction.id)
    if hasattr(transaction, 'id') and transaction.id:
        # 기존 트랜잭션 조회
        existing_transaction = db.query(Transaction).get(transaction.id)
        if existing_transaction:
            # 기존 트랜잭션 업데이트
            existing_transaction.date = transaction.date
            existing_transaction.asset_id = transaction.asset_id
            existing_transaction.type = asset_type + '_SELL'
            existing_transaction.quantity = transaction.quantity
            existing_transaction.price = transaction_metadata['bought_price']
            existing_transaction.amount = transaction_metadata['bought_amount']
            existing_transaction.currency = transaction.currency
            existing_transaction.debit_account_id = transaction.debit_account_id
            existing_transaction.credit_account_id = transaction.credit_account_id
            existing_transaction.fees = transaction.fees
            existing_transaction.transaction_metadata = {}
            
            db.add(existing_transaction)
            db.commit()
            db.refresh(existing_transaction)
            return existing_transaction
    
    # ID가 없거나 기존 트랜잭션이 없는 경우 새로 생성
    sell_transaction = Transaction(
        date=transaction.date,
        asset_id=transaction.asset_id,
        type=asset_type + '_SELL',
        quantity=transaction.quantity,
        price=transaction_metadata['bought_price'],
        amount=transaction_metadata['bought_amount'],
        currency=transaction.currency,
        debit_account_id=transaction.debit_account_id,
        credit_account_id=transaction.credit_account_id,
        fees=transaction.fees,
        username=username,
        transaction_metadata={}
    )
    
    return sell_transaction


def datetime_to_str(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

def get_total_fees(fees):
    total_fees = 0
    for fee_code, fee_data in fees.items():
        total_fees += fee_data['amount']
    return total_fees

def get_transaction_all(db, username):
    transaction_all = db.query(Transaction).filter(Transaction.username == username).all()
    return transaction_all

def get_transaction_by_asset_id(db, asset_id, username):
    transaction = db.query(Transaction).filter(
            Transaction.asset_id == asset_id, 
            Transaction.username == username
        ).all()
    return transaction

def get_asset_quantity(db, asset_id, username):
    transaction = get_transaction_by_asset_id(db, asset_id, username)
    quantity = 0
    for tx in transaction:
        if 'BUY' in tx.type.upper():
            quantity += tx.quantity
        elif 'SELL' in tx.type.upper():
            quantity -= tx.quantity
    return quantity


def create_security_transaction_v2(
        db: Session,
        transaction: schemas.SecurityTransactionCreate,
        username: str,
    ):
    
    
    
    if 'BUY' in transaction.type.upper():
        create_buy_transaction_v2(db, transaction, username)
    
    elif 'SELL' in transaction.type.upper():
        create_sell_transaction_v2(db, transaction, username)
    

def create_buy_transaction_v2(db, transaction, username):
    
    print('buy_data:', transaction.fees)
    asset = crud_asset.get_asset_by_id(db, transaction.asset_id, username)
    crud_asset.turn_on_is_active(db, transaction.asset_id, username)
    
    asset_type = asset.type.upper()

    
    # 취득원가 계산
    total_fees = get_total_fees(transaction.fees)
    print('total_fees:', total_fees)
    acquisition_cost = transaction.amount + total_fees
    print('acquisition_cost:', acquisition_cost)

    # 주식 매수 거래 기록 (취득원가 기준)
    buy_transaction = Transaction(
        date=transaction.date,
        type=asset_type + '_BUY',
        asset_id=transaction.asset_id,
        quantity=transaction.quantity,
        price=acquisition_cost / transaction.quantity,  # 단가는 취득원가 기준
        amount=acquisition_cost,  # 총액은 취득원가
        currency=transaction.currency,
        debit_account_id=transaction.debit_account_id,       # 주식자산 증가 (취득원가)
        credit_account_id=transaction.credit_account_id,  # 현금성자산 감소
        fees=transaction.fees,
        transaction_metadata={
            "fifo": {
                "quantity": transaction.quantity,
            },
        },
        username=username
    )
    db.add(buy_transaction)
    db.flush()
    db.commit()

    print('buy_transaction:', buy_transaction.__dict__)
 

def create_sell_transaction_v2(db, transaction, username):
    
    # 보유량 조회
    print('transaction:', transaction.id, transaction.quantity)
    asset_quantity, fifo_amount, average_price = crud_asset.get_asset_info_by_asset_id(db, transaction.asset_id, username)
    print('asset_quantity:', asset_quantity)
    if asset_quantity < transaction.quantity:
        transaction.quantity = asset_quantity
    elif asset_quantity == 0:
        crud_asset.turn_off_is_active(db, transaction.asset_id, username)
        raise HTTPException(status_code=400, detail="보유량이 없습니다.")
    
    asset = crud_asset.get_asset_by_id(db, transaction.asset_id, username)
    asset_type = asset.type.upper()
    
    # fifo 매도 계산
    transaction_metadata, tx_transactions = calculate_fifo_sell(db, transaction, username)
    # pprint(transaction_metadata)
    # 매도 금액, 수수료, 원금 계산
    sell_amount = transaction_metadata['sell_amount']
    total_fee = transaction_metadata['total_fee']
    original_cost = transaction_metadata['bought_amount']
    pl_amount = sell_amount - total_fee - original_cost
    
    # 1. 기본 매도 거래
    sell_transaction = create_or_update_sell_transaction(
        db, 
        transaction, 
        asset_type, 
        transaction_metadata, 
        username
    )

    # if not hasattr(sell_transaction, 'id'):
    #     db.add(sell_transaction)
    #     db.commit()
    #     db.refresh(sell_transaction)
    # else:
    #     db.commit()
    db.add(sell_transaction)
    db.flush()
    # sell_transaction.transaction_metadata['fees'] = transaction.fees 
    sell_transaction.transaction_metadata = transaction_metadata
    flag_modified(sell_transaction, "transaction_metadata")
    
    
    # 2. 매매손익 처리
    if pl_amount > 0:  # 매매이익
        pl_transaction = Transaction(
            date=transaction.date,
            asset_id=transaction.asset_id,
            type=asset_type + '_SELL_PROFIT',
            amount=abs(transaction_metadata['profit_loss']),
            currency=transaction.currency,
            debit_account_id=transaction.debit_account_id,  # 현금 증가
            credit_account_id=crud_account.get_account_by_code(db, "5301", username).id,  # 매매차익
            username=username,
            transaction_metadata={}
        )
        
        # # 이익의 이익잉여금 반영
        # retained_pl = Transaction(
        #     date=transaction.date,
        #     asset_id=transaction.asset_id,
        #     type=asset_type + '_SELL_PROFIT_RETAINED',
        #     amount=abs(transaction_metadata['profit_loss']),
        #     currency=transaction.currency,
        #     debit_account_id=crud_account.get_account_by_code(db, "5101", username).id,  # 매매차익 감소
        #     credit_account_id=crud_account.get_account_by_code(db, "3002", username).id,  # 이익잉여금 증가
        #     username=username,
        #     transaction_metadata={}
        # )
    
    else:  # 매매손실
        pl_transaction = Transaction(
            date=transaction.date,
            asset_id=transaction.asset_id,
            type=asset_type + '_SELL_LOSS',
            amount=abs(transaction_metadata['profit_loss']),
            currency=transaction.currency,
            debit_account_id=crud_account.get_account_by_code(db, "4301", username).id,  # 매매손실
            credit_account_id=transaction.debit_account_id,
            username=username,
            transaction_metadata={}
        )
        
        # # 손실의 이익잉여금 반영
        # retained_pl = Transaction(
        #     date=transaction.date,
        #     asset_id=transaction.asset_id,
        #     type=asset_type + '_SELL_LOSS_RETAINED',
        #     amount=abs(transaction_metadata['profit_loss']),
        #     currency=transaction.currency,
        #     debit_account_id=crud_account.get_account_by_code(db, "3002", username).id, # 이익잉여금 감소
        #     credit_account_id=crud_account.get_account_by_code(db, "4103", username).id, # 매매손실 증가
        #     username=username,
        #     transaction_metadata={}
        # )
        
        
    for tx in tx_transactions:
        if 'main_transaction' not in tx.transaction_metadata['fifo']:
            tx.transaction_metadata['fifo']['main_transaction'] = []
        
        # print('tx:', tx.transaction_metadata['fifo']['quantity'])
        # print('tx:', tx.quantity)
        # print('tx:', tx.quantity - tx.transaction_metadata['fifo']['quantity'])
        # print('tx:', tx.transaction_metadata)
        tx.transaction_metadata['fifo']['main_transaction'].append({'id':sell_transaction.id, 'sold_quantity':tx.quantity - tx.transaction_metadata['fifo']['quantity']})
        # print('tx:', tx.transaction_metadata['fifo'])
        flag_modified(tx, "transaction_metadata")
        db.add(tx)
    fees_id = []
    if transaction.fees:
        for fee_code, fee_data in transaction.fees.items():
            # 수수료 거래
            fee_transaction = Transaction(
                date=transaction.date,
                asset_id=transaction.asset_id,
                type=asset_type + '_SELL_FEE',
                amount=fee_data['amount'],
                currency=fee_data['currency'],
                debit_account_id=fee_data['id'],
                credit_account_id=transaction.debit_account_id,
                username=username,
                transaction_metadata={
                    'transactions_id': sell_transaction.id,
                }
            )
            
            # # 이익잉여금 반영
            # retained_fee = Transaction(
            #     date=transaction.date,
            #     asset_id=transaction.asset_id,
            #     type=asset_type + '_SELL_FEE_RETAINED',
            #     amount=fee_data['amount'],
            #     currency=fee_data['currency'],
            #     debit_account_id=crud_account.get_account_by_code(db, "3002", username).id,
            #     credit_account_id=fee_data['id'],
            #     username=username,
            #     transaction_metadata={
            #         'transactions_id': sell_transaction.id,
            #     }
            # )
            # db.add(retained_fee)
            # fees_id.append(retained_fee.id)
            
            db.add(fee_transaction)
            db.flush()
            
            fees_id.append(fee_transaction.id)
        
        
    db.add(pl_transaction)
    # db.add(retained_pl)
    db.flush()
    pl_transaction.transaction_metadata['transactions_id'] = sell_transaction.id
    # retained_pl.transaction_metadata['transactions_id'] = sell_transaction.id
    flag_modified(pl_transaction, "transaction_metadata")
    # flag_modified(retained_pl, "transaction_metadata")
    sell_transaction.transaction_metadata['transactions_id'].extend(fees_id)
    sell_transaction.transaction_metadata['transactions_id'].append(pl_transaction.id)
    # sell_transaction.transaction_metadata['transactions_id'].append(retained_pl.id)
    flag_modified(sell_transaction, "transaction_metadata")
    # print('sell_transaction:', sell_transaction.transaction_metadata)
    # db.add(sell_transaction)
    
    
    
    pprint(sell_transaction.transaction_metadata)
    
    db.commit()
    db.refresh(sell_transaction)
    
    asset_quantity, fifo_amount, average_price = crud_asset.get_asset_info_by_asset_id(db, transaction.asset_id, username)
    print('asset_quantity:', asset_quantity)
    if asset_quantity == 0:
        crud_asset.turn_off_is_active(db, transaction.asset_id, username)
    






def create_security_transaction(
        db: Session,
        transaction: schemas.SecurityTransactionCreate,
        username: str,
    ):
    # 포지션 조회
    position = crud_position.get_position_by_asset_id(db=db, username=username, asset_id=transaction.asset_id)
    # 보유량이 없는 경우 오류 처리
    if not position:
        raise HTTPException(status_code=400, detail="매도할 자산이 없습니다.")
    else:
        # 보유량이 매도량보다 적은 경우 매도량 조정
        if position.quantity < transaction.quantity:
            transaction.quantity = position.quantity
    
    # 자산 정보 조회
    asset = db.query(Asset).filter(Asset.id == transaction.asset_id).first()
    print('asset type:', asset.type)
    _type = asset.type.upper()
    # 자산 정보가 없는 경우 오류 처리
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # 거래 통화와 자산 통화가 다른 경우 환율 필수 체크
    fee_currency = None
    for fee in transaction.fees:
        if transaction.currency != transaction.fees[fee]['currency']:
            raise HTTPException(
                status_code=400,
                detail="모든 수수료는 거래 통화와 동일한 통화로 입력해야 합니다."
            )
    if transaction.currency != asset.currency and not transaction.exchange_rate:
        raise HTTPException(
            status_code=400, 
            detail=f"거래 통화와 자산 통화가 다릅니다. 거래 통화: {transaction.currency}, 자산 통화: {asset.currency}"
        )
    
    
    # 정상 처리 ############################################################
    # 1. 메인 거래 생성
    total_fees_original = 0
    if transaction.fees:
        for fee_code, fee_data in transaction.fees.items():
            total_fees_original += fee_data['amount']
            
    if 'BUY' in transaction.type.upper():
        buy_transaction = Transaction(
            date=convert_to_kst(transaction.date),
            asset_id=transaction.asset_id,
            type=_type + '_BUY',
            currency=transaction.currency,
            amount=transaction.amount,
            username=username,
            debit_account_id=transaction.debit_account_id,
            credit_account_id=transaction.credit_account_id,
            transaction_metadata={
                'fifo': {
                    'quantity': transaction.quantity,
                    'main_transaction': [],
                },
            },
            quantity=transaction.quantity,
            price=transaction.price,
            exchange_rate=transaction.exchange_rate,
            note=transaction.note,
        )
        db.add(buy_transaction)
        db.flush()     
        

        buy_transaction.amount = transaction.amount + total_fees_original
        transaction_type = "WITHDRAWAL"
    else:
        transaction_type = "DEPOSIT"
        
    crud_cash_balance.update_cash_balance(
        db=db,
        username=username,
        currency=transaction.currency,
        amount=transaction.amount,
        transaction_type=transaction_type,
        exchange_rate=transaction.exchange_rate
    )

    # 4. 포지션 업데이트 (자산 통화 기준)
    update_security_position(
        db=db,
        username=username,
        asset_id=transaction.asset_id,
        quantity=transaction.quantity,
        price=transaction.price,
        transaction_type=transaction.type,
        original_currency=transaction.currency,
        exchange_rate=transaction.exchange_rate
    )

    if 'BUY' in transaction.type.upper():
        db.commit()
        return security_transaction_response(buy_transaction)

    # 매도 거래인 경우 FIFO 실현 손익 계산 ################################ 
    
    if 'SELL' in transaction.type.upper():
        
        
        # 과거 매수 거래 조회
        buy_transactions_v2 = get_historical_buys_v2(db, username, transaction.asset_id)
        if not buy_transactions_v2:
            db.rollback()
            raise HTTPException(status_code=400, detail="매도할 자산이 없습니다. buy_transactions_v2:")
        transaction_metadata, tx_transactions = calculate_fifo_sell(db, transaction, buy_transactions_v2, username)
        total_buy_amount = transaction_metadata['bought_amount']
        
        # 1. 원금 회수 거래 생성
        principal_transaction = Transaction(
            date=transaction.date,
            type=_type + '_PRINCIPAL_RECOVERY',
            asset_id=transaction.asset_id,
            quantity=transaction.quantity,
            price=transaction.price,
            currency=transaction.currency,
            amount=total_buy_amount,  # FIFO로 계산된 매수 원가
            username=username,
            debit_account_id=transaction.debit_account_id,  # 현금 증가, 현금 계좌
            credit_account_id=transaction.credit_account_id,  # 주식 감소, 주식 계좌
            transaction_metadata={
                'fee_transactions': [],
            }
        )
        db.add(principal_transaction)
        db.flush()

        # 2. 매매손익 거래 생성
        trading_pl = transaction.amount - total_buy_amount
        # if trading_pl != 0:  # 손익이 있는 경우만 생성
        pl_transaction = Transaction(
            date=transaction.date,
            type=_type + '_TRADING_PL',
            asset_id=transaction.asset_id,
            quantity=transaction.quantity,
            price=abs(trading_pl) / transaction.quantity,
            currency=transaction.currency,
            amount=abs(trading_pl),
            username=username,
            debit_account_id=(
                transaction.debit_account_id if trading_pl > 0
                else crud_account.get_account_by_code(db, "4103", username).id  # 매매 손실
            ),
            credit_account_id=(
                crud_account.get_account_by_code(db, "5101", username).id if trading_pl > 0  # 매매 이익
                else transaction.debit_account_id
            ),
            transaction_metadata={
                # 'transaction_id': principal_transaction.id,
                # 'transaction_type': _type + '_TRADING_PL',
                'pl_type': 'PROFIT' if trading_pl > 0 else 'LOSS',
                'fee_transactions': [],
                'fee': total_fees_original,
                'fifo': {
                    'summary': [],
                },
            }
        )
        db.add(pl_transaction)
        db.flush()
        
        
        
        for tx in tx_transactions:
            print('tx:', tx.transaction_metadata)
            tx.transaction_metadata['fifo']['main_transaction'].append(pl_transaction.id)
            flag_modified(tx, "transaction_metadata")
            db.add(tx)
            db.flush()
            
        fee_transactions = get_fee_transaction_id(db, username, transaction, principal_transaction.id, pl_transaction.id)
    
        # transaction_metadata = calculate_fifo_sell(db, principal_transaction, username)
        
        
        principal_transaction.transaction_metadata['transactions_id'] = pl_transaction.id        
        flag_modified(principal_transaction, "transaction_metadata")
        pl_transaction.transaction_metadata['transactions_id'] = principal_transaction.id        
        pl_transaction.transaction_metadata['fee_transactions'] = fee_transactions
        pl_transaction.transaction_metadata['fee'] = total_fees_original
        pl_transaction.transaction_metadata['fifo'] = {}
        pl_transaction.transaction_metadata['fifo']['summary'] = []
        pl_transaction.transaction_metadata['fifo']['quantity'] = transaction_metadata['quantity']
        pl_transaction.transaction_metadata['fifo']['bought_amount'] = transaction_metadata['bought_amount']
        pl_transaction.transaction_metadata['fifo']['bought_price'] = transaction_metadata['bought_price']
        pl_transaction.transaction_metadata['fifo']['sell_amount'] = transaction_metadata['sell_amount']
        pl_transaction.transaction_metadata['fifo']['sell_quantity'] = transaction_metadata['sell_quantity']
        pl_transaction.transaction_metadata['fifo']['sell_price'] = transaction_metadata['sell_price']
        pl_transaction.transaction_metadata['fifo']['profit_loss'] = transaction_metadata['profit_loss']
        pl_transaction.transaction_metadata['fifo']['profit_loss_rate'] = transaction_metadata['profit_loss_rate']
        pl_transaction.transaction_metadata['fifo']['sell_transactions'] = transaction_metadata['sell_transactions']
        # pl_transaction.transaction_metadata['fifo']['total_fee'] = transaction_metadata['total_fee']
        # pl_transaction.transaction_metadata['fifo']['total_fees'] = transaction_metadata['total_fees']
        pl_transaction.transaction_metadata['fifo']['summary'] = transaction_metadata['summary']
        flag_modified(pl_transaction, "transaction_metadata")
        
        # 매도 거래 생성 후 거래 정보만 조회
        if transaction.get_info:
            db.rollback()
            return pl_transaction.transaction_metadata
        
        db.commit()
        return security_transaction_response(pl_transaction)




def get_fee_transaction_id(db, username, transaction, principal_transaction_id, pl_transaction_id):
    # 수수료 처리
    fee_transactions = []
    if transaction.fees:
        for fee_code, fee_data in transaction.fees.items():
            fee_currency = fee_data.get('currency', transaction.currency)
            fee_amount = fee_data['amount']

            fee_transaction = Transaction(
                date=convert_to_kst(transaction.date),
                asset_id=transaction.asset_id,
                type='FEE',
                currency=fee_currency,
                amount=fee_amount,
                debit_account_id=int(fee_data['id']),
                credit_account_id=transaction.credit_account_id,
                note=f"거래 수수료: {fee_data.get('name', '')}",
                username=username,
                transaction_metadata={
                    'transaction_type': 'SECURITY_FEE',
                    'transactions_id': {
                        'principal': principal_transaction_id,
                        'pl': pl_transaction_id,
                    },
                    'fee_type': fee_code,
                }
            )
            db.add(fee_transaction)
            db.flush()
            fee_transactions.append(fee_transaction.id)

            # 수수료에 대한 현금 잔액 업데이트
            crud_cash_balance.update_cash_balance(
                db=db,
                username=username,
                currency=fee_currency,
                amount=fee_amount,
                transaction_type="WITHDRAWAL",
                exchange_rate=transaction.exchange_rate
        )
            
    return fee_transactions


def calculate_fifo_sell(
        db: Session,
        transaction: Transaction,
        # buy_transactions_v2: List[Transaction],
        username: str,
        get_info: bool = False,
    ):
    print('transaction==================================================')
    pprint(transaction)
    buy_transactions_v2 = get_historical_buys_v2(db, username, transaction.asset_id)
    
    sell_transactions = []
    total_bought_amount = 0
    total_sell_amount = 0
    summary = []
    # total_fee = 0
    # total_fees = []
    sell_quantity = transaction.quantity
    tx_transactions_id = []
    tx_transactions = []
    
    for tx in buy_transactions_v2:
        
        fifo_quantity = tx.transaction_metadata['fifo']['quantity']
        # print('fifo_quantity:', fifo_quantity)
        sell_quantity -= fifo_quantity  # 매도 수량 계산
        # print('sell_quantity:', sell_quantity)
        
        # 매도 수량 계산
        if sell_quantity > 0:   # 매도 수량이 양수인 경우
            fifo_sell_quantity = fifo_quantity
            
        elif sell_quantity == 0:  # 매도 수량이 0인 경우
            fifo_sell_quantity = fifo_quantity
        
        elif sell_quantity < 0:  # 매도 수량이 음수인 경우
            fifo_sell_quantity = fifo_quantity + sell_quantity
        
        sell_transactions.append(tx.id) # 매도 거래 ID 추가
        total_bought_amount += fifo_sell_quantity * tx.price # 매도 수량 계산
        total_sell_amount += fifo_sell_quantity * transaction.price
        # print('total_bought_amount:', total_bought_amount)
        # print('total_sell_amount:', total_sell_amount)
        
        # total_fee += tx.transaction_metadata['total_fees'] * fifo_sell_quantity / tx.quantity # 수수료 계산
        # total_fees.extend(tx.transaction_metadata['fee_transactions']) # 수수료 거래 ID 추가

        # 매도후 남은 수량 업데이트
        fifo_balance = abs(fifo_quantity - fifo_sell_quantity)
        tx.transaction_metadata['fifo']['quantity'] = fifo_balance
        # 매도 거래 ID 매도 수량 업데이트
        # tx.transaction_metadata['fifo']['main_transaction'].append(transaction.id)
        flag_modified(tx, "transaction_metadata")
        tx_transactions_id.append(tx.id)
        tx_transactions.append(tx)
        
        summary.append({
            'id': tx.id,
            'date': tx.date.isoformat(),    
            'holding_days': (datetime.now() - tx.date).days,
            'bought_quantity': tx.quantity,
            'bought_amount': fifo_sell_quantity * tx.price,
            'bought_price': tx.price,
            'sell_quantity': fifo_sell_quantity,
            'sell_amount': fifo_sell_quantity * transaction.price,
            'sell_price': transaction.price,
            # 'fee': tx.transaction_metadata['total_fees'] * fifo_sell_quantity / tx.quantity,
            # 'fees': tx.transaction_metadata['fee_transactions'],
            'realized_pl': (fifo_sell_quantity * transaction.price) - (fifo_sell_quantity * tx.price),
            'realized_pl_rate': (fifo_sell_quantity * transaction.price - fifo_sell_quantity * tx.price) / (fifo_sell_quantity * tx.price),
        })
        flag_modified(tx, "transaction_metadata")
 
        # db.add(tx)
        # db.flush()

        # print('fifo_sell_quantity :', fifo_sell_quantity*db_transaction.price)
        # print('total_bought_amount:', total_bought_amount)
        if sell_quantity == 0 or sell_quantity < 0:
            break
    if get_info:
        db.rollback()
    
    total_fee = 0
    if transaction.fees:
        for fee_code, fee_data in transaction.fees.items():
            total_fee += fee_data['amount']
    # print('transaction==============', transaction.id, transaction.quantity)
    if transaction.quantity > 0:
        bought_price = total_bought_amount / transaction.quantity
        profit_loss_rate = (total_sell_amount - total_bought_amount) / total_bought_amount
    else:
        bought_price = 0
        profit_loss_rate = 0
    result = {
        'quantity': transaction.quantity,
        'bought_amount': total_bought_amount,
        'bought_price': bought_price,
        'sell_amount': total_sell_amount,
        # 'sell_quantity': transaction.quantity,
        'total_fee': total_fee,
        'sell_price': transaction.price,
        'profit_loss': total_sell_amount - total_bought_amount,
        'profit_loss_rate': profit_loss_rate,
        'transactions_id': sell_transactions,
        'summary': summary,
    }
    # pprint(result)
    return result, tx_transactions








def calculate_fifo_sell_info(db, username, asset_id, quantity, price, fees=0, get_info=False):
       
    buy_transactions_v2 = get_historical_buys_v2(db, username, asset_id)   
    position = crud_position.get_position_by_symbol(db, username, asset_id)
    if not position:
        db.rollback()
        raise HTTPException(status_code=400, detail="매도할 자산이 없습니다.")
    else:
        if position.quantity < quantity:
            quantity = position.quantity
    
    sell_transactions = []
    total_buy_amount = 0
    summary = []
    total_fee = 0
    total_fees = []
    sell_quantity = quantity
    print('sell_quantity:', sell_quantity)
    
    for tx in buy_transactions_v2:
        
        fifo_quantity = tx.transaction_metadata['fifo']['quantity']
        print('fifo_quantity:', fifo_quantity)
        sell_quantity -= fifo_quantity
        print('sell_quantity:', sell_quantity)
        
        
        if sell_quantity > 0:
            fifo_sell_quantity = fifo_quantity
            
        elif sell_quantity == 0:
            fifo_sell_quantity = fifo_quantity
        
        elif sell_quantity < 0:
            fifo_sell_quantity = fifo_quantity + sell_quantity
        
        
        sell_transactions.append(tx.id)
        total_buy_amount += fifo_sell_quantity * tx.price
        total_fee += tx.transaction_metadata['total_fees'] * fifo_sell_quantity / tx.quantity
        total_fees.extend(tx.transaction_metadata['fee_transactions'])
        
        # # 매도후 남은 수량 업데이트
        # tx.transaction_metadata['fifo']['quantity'] = fifo_quantity - fifo_sell_quantity
        # # 매도 거래 ID 매도 수량 업데이트
        # tx.transaction_metadata['fifo']['main_transaction'].append(transaction.id)
        # flag_modified(tx, "transaction_metadata")
        summary.append({
            'id': tx.id,
            'date': tx.date.isoformat(),
            'holding_days': (datetime.now() - tx.date).days,
            'buy_quantity': tx.quantity,
            'buy_price': tx.price,
            'buy_currency': tx.currency,
            'quantity': fifo_sell_quantity,
            'buy_amount': fifo_sell_quantity * tx.price,
            'sell_amount': fifo_sell_quantity * price,
            'fee': total_fee,
            'fees': total_fees,
            'realized_pl': (fifo_sell_quantity * price) - (fifo_sell_quantity * tx.price),
            'realized_pl_rate': (fifo_sell_quantity * price - fifo_sell_quantity * tx.price) / (fifo_sell_quantity * tx.price),
        })
        
        
        if sell_quantity == 0 or sell_quantity < 0:
            break

    
    if get_info:
        db.rollback()
    return {
        'asset_id': asset_id,
        'quantity': quantity,
        'buy_amount': total_buy_amount,
        'buy_price': total_buy_amount / quantity,
        'sell_amount': quantity * price,
        'sell_price': price,
        'profit_loss': quantity * price - total_buy_amount,
        'profit_loss_rate': (quantity * price - total_buy_amount) / total_buy_amount,
        'sell_transactions': sell_transactions,
        'total_fee': total_fee + fees,
        'summary': summary,
    }



    # except Exception as e:
    #     db.rollback()
    #     raise HTTPException(status_code=400, detail=str(e))







def calculate_realized_profit_loss(
    position: Position,
    sell_quantity: float,
    sell_price: float,
    sell_currency: str,
    exchange_rate: float = None
) -> Dict[str, float]:
    """매도 시 실현 손익 계산"""
    # 평균 매수가로 계산
    avg_cost = position.avg_price
    
    # 통화가 다른 경우 환율 적용
    if sell_currency != position.currency and exchange_rate:
        sell_price_converted = sell_price / exchange_rate
    else:
        sell_price_converted = sell_price

    realized_pl = (sell_price_converted - avg_cost) * sell_quantity
    
    return {
        'realized_profit_loss': realized_pl,
        'avg_cost': avg_cost,
        'sell_price_converted': sell_price_converted,
        'original_currency': sell_currency,
        'position_currency': position.currency,
        'exchange_rate': exchange_rate
    }

def get_historical_buys(
    db: Session,
    username: str,
    asset_id: int
) -> List[Transaction]:
    """해당 자산의 매수 거래 내역을 날짜순으로 조회"""
    return db.query(Transaction).filter(
        Transaction.username == username,
        Transaction.asset_id == asset_id,
        Transaction.type.in_(['STOCK_BUY', 'CRYPTO_BUY'])
    ).order_by(Transaction.date.asc()).all()


def get_historical_buys_v2(
        db: Session,
        username: str,
        asset_id: int
    ) -> List[Transaction]:
    
    """해당 자산의 매수 거래 내역을 날짜순으로 조회"""
    
    # fifo.quantity가 0인 거래들을 날짜순으로 정렬하여 가져오기
    return db.query(Transaction).filter(
        Transaction.username == username,
        Transaction.asset_id == asset_id,
        Transaction.type.ilike('%BUY%'),
        cast(Transaction.transaction_metadata['fifo']['quantity'], Float) != 0
    ).order_by(
        Transaction.date.asc(),
        Transaction.id.asc()
    ).all()
    
    # # 마지막 거래 (가장 최근 거래) 가져오기
    # last_zero_fifo = zero_fifo_transactions[-1] if zero_fifo_transactions else None
    # # 해당 거래 이후의 모든 매수 거래 조회
    # query = db.query(Transaction).filter(
    #     Transaction.username == username,
    #     Transaction.asset_id == asset_id,
    #     Transaction.type.ilike('%BUY%')
    # )
    # if last_zero_fifo:
    #     query = query.filter(Transaction.date > last_zero_fifo.date)
    
    # return query.order_by(
    #     Transaction.date.asc(),
    #     Transaction.id.asc()
    # ).all()


def calculate_fifo_profit_loss(
        buy_transactions: List[Transaction],
        sell_quantity: float,
        sell_price: float,
    ) -> Dict[str, Any]:
    
    
    """FIFO 방식으로 실현 손익 계산"""
    
    # 매도 수량 변수 초기화
    remaining_sell_quantity = sell_quantity  # 매도 수량
    total_realized_pl = 0  # 실현 손익
    realized_details = []  # 실현 손익 상세
    used_transactions = []  # 사용된 거래들
    
    for buy_tx in buy_transactions:
        if remaining_sell_quantity <= 0:
            break

        # 이미 매도된 수량 계산
        previously_sold = sum(
            detail.get('quantity', 0)
            for detail in buy_tx.transaction_metadata.get('sold_details', [])
        ) if buy_tx.transaction_metadata and 'sold_details' in buy_tx.transaction_metadata else 0

        available_quantity = buy_tx.quantity - previously_sold

        if available_quantity <= 0:
            continue

        # 이번에 매도할 수량 계산
        quantity_to_sell = min(remaining_sell_quantity, available_quantity)
        
        # # 매수 가격을 매도 통화로 변환
        # if buy_tx.currency != sell_currency and exchange_rate:
        #     buy_price_converted = buy_tx.price * exchange_rate
        # else:
        #     buy_price_converted = buy_tx.price

        # 실현 손익 계산
        realized_pl = (sell_price - buy_tx.price) * quantity_to_sell
        
        realized_detail = {
            'buy_transaction_id': buy_tx.id,    # 매수 거래 ID
            'buy_date': buy_tx.date.isoformat(), # 매수 일자
            'buy_price': buy_tx.price, # 매수 가격
            'buy_currency': buy_tx.currency, # 매수 통화
            'quantity': quantity_to_sell, # 매도 수량
            'realized_pl': realized_pl, # 실현 손익
            'holding_days': (datetime.now() - buy_tx.date).days # 보유 일수
        }
        realized_details.append(realized_detail)
        used_transactions.append({
            'transaction': buy_tx,
            'used_quantity': quantity_to_sell
        })
        total_realized_pl += realized_pl
        remaining_sell_quantity -= quantity_to_sell

    if remaining_sell_quantity > 0:
        raise HTTPException(
            status_code=400,
            detail=f"매도 가능 수량이 부족합니다. 부족 수량: {remaining_sell_quantity}"
        )

    return {
        'realized_profit_loss': total_realized_pl,  # 실현 손익
        'realized_details': realized_details,    # 실현 손익 상세
        'used_transactions': used_transactions  # 사용된 거래들
    }


def update_security_position(
    db: Session,
    username: str,
    asset_id: int,
    quantity: float,
    price: float,
    transaction_type: str,
    original_currency: str = None,
    exchange_rate: float = None
):
    """증권/암호화폐 포지션 업데이트"""
    position = db.query(Position).filter(
        Position.username == username,
        Position.asset_id == asset_id
    ).first()
    
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    
    if not position:
        position = Position(
            username=username,
            asset_id=asset_id,
            currency=asset.currency,
            quantity=0,
            avg_price=0,
            current_price=price,
            last_updated=get_current_kst_time(),
            position_metadata={
                'transactions_count': 0,
                'total_buy_quantity': 0,
                'total_sell_quantity': 0,
                'total_buy_amount': 0,
                'total_sell_amount': 0,
                'original_currency': original_currency,
                'last_exchange_rate': exchange_rate
            }
        )
        db.add(position)
    
    amount = quantity * price
    
    if transaction_type in ['STOCK_BUY', 'CRYPTO_BUY']:
        # 매수 시 평균단가 계산
        total_value = (position.quantity * position.avg_price) + amount
        position.quantity += quantity
        position.avg_price = total_value / position.quantity if position.quantity > 0 else price
        position.position_metadata['total_buy_quantity'] = position.position_metadata.get('total_buy_quantity', 0) + quantity
        position.position_metadata['total_buy_amount'] = position.position_metadata.get('total_buy_amount', 0) + amount
    else:
        # 매도 시
        position.quantity -= quantity
        position.position_metadata['total_sell_quantity'] = position.position_metadata.get('total_sell_quantity', 0) + quantity
        position.position_metadata['total_sell_amount'] = position.position_metadata.get('total_sell_amount', 0) + amount
    
    position.current_price = price
    position.last_updated = get_current_kst_time()
    position.position_metadata['transactions_count'] = position.position_metadata.get('transactions_count', 0) + 1
    position.position_metadata['original_currency'] = original_currency
    position.position_metadata['last_exchange_rate'] = exchange_rate
    
    flag_modified(position, "position_metadata")

def security_transaction_response(transaction: Transaction) -> Dict[str, Any]:
    
    """거래 응답을 스키마에 맞게 변환"""
    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )
    if isinstance(transaction, dict):
        transaction_dict = transaction
    
    else:
        # SQLAlchemy 모델을 딕셔너리로 변환
        transaction_dict = {
            column.name: getattr(transaction, column.name)
            for column in transaction.__table__.columns
        }

        # asset 정보를 딕셔너리로 변환
        if hasattr(transaction, 'asset') and transaction.asset:
            asset_dict = {
                'id': transaction.asset.id,
                'name': transaction.asset.name,
                'symbol': transaction.asset.symbol,
                'type': transaction.asset.type,
                'currency': transaction.asset.currency,
                'exchange': transaction.asset.exchange,
                'asset_metadata': transaction.asset.asset_metadata
            }
        else:
            asset_dict = None

        transaction_dict['asset'] = asset_dict

    # datetime 객체를 ISO 형식 문자열로 변환
    if 'date' in transaction_dict and isinstance(transaction_dict['date'], datetime):
        transaction_dict['date'] = transaction_dict['date'].isoformat()
    if 'created_at' in transaction_dict and isinstance(transaction_dict['created_at'], datetime):
        transaction_dict['created_at'] = transaction_dict['created_at'].isoformat()

    return transaction_dict

def get_account_id(db: Session, account_name: str) -> int:
    """계정 ID 조회"""
    return db.query(Account).filter(Account.name == account_name).first().id

def update_security_valuation(
    db: Session,
    username: str,
    asset_id: int,
    current_price: float,
    valuation_date: datetime = None
):
    """주식 평가손익 계산 및 기록"""
    try:
        # 포지션 조회
        position = db.query(Position).filter(
            Position.username == username,
            Position.asset_id == asset_id
        ).first()

        if not position or position.quantity <= 0:
            return None

        # 평가손익 계산
        previous_price = position.current_price
        valuation_pl = (current_price - previous_price) * position.quantity

        # 평가손익 거래 생성
        transaction = Transaction(
            date=valuation_date or get_current_kst_time(),
            type="VALUATION",
            asset_id=asset_id,
            quantity=position.quantity,
            price=current_price,
            currency=position.currency,
            amount=valuation_pl,
            username=username,
            # 평가이익인 경우
            debit_account_id=get_account_id("주식투자"), # 자산 증가
            credit_account_id=get_account_id("주식평가이익"), # 평가이익 증가
            # 평가손실인 경우 반대로 처리
            transaction_metadata={
                'valuation_type': 'MARK_TO_MARKET',
                'previous_price': previous_price,
                'price_change': current_price - previous_price,
                'position_quantity': position.quantity
            }
        )

        db.add(transaction)
        
        # 포지션 정보 업데이트
        position.current_price = current_price
        position.position_metadata['last_valuation_date'] = valuation_date.isoformat()
        position.position_metadata['valuation_pl'] = valuation_pl
        flag_modified(position, "position_metadata")

        db.commit()
        return transaction

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


