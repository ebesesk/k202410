from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import func, and_, cast, Float, JSON, text
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.models.investment_models import Asset, Transaction
from app.schemas import investment_schemas_v2 as schemas

from app.utils.utils import get_current_kst_time, convert_to_kst

from pprint import pprint


def get_asset_by_id(db: Session, asset_id: int, username: str):
    return db.query(Asset).filter(Asset.id == asset_id, Asset.username == username).first()

def get_asset_by_symbol(db: Session, symbol: str, username: str):
    return db.query(Asset).filter(Asset.symbol == symbol, Asset.username == username).first()

def turn_on_is_active(db: Session, asset_id: int, username: str):
    asset = get_asset_by_id(db, asset_id, username)
    asset.is_active = True
    db.commit()
    db.refresh(asset)
    return asset

def turn_off_is_active(db: Session, asset_id: int, username: str):
    asset = get_asset_by_id(db, asset_id, username)
    asset.is_active = False
    db.commit()
    db.refresh(asset)
    return asset

def get_asset_is_active(db: Session, username: str):
    return db.query(Asset).outerjoin(
        Transaction
    ).filter(
        Asset.username == username,  
        Asset.is_active == True
    ).all()
    
def get_transaction_by_asset_id(db, asset_id, username):
    transaction = db.query(Transaction).filter(
            Transaction.asset_id == asset_id, 
            Transaction.username == username
        ).all()
    return transaction


# 보유량 조회
def get_asset_info_by_asset_id(db, asset_id, username, date=None):
    '''
    보유량 조회
    '''
    if date and isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    transaction = get_transaction_by_asset_id(db, asset_id, username)
    total_quantity = 0
    fifo_amount = 0
    for tx in transaction:
        if not date:
            if tx.quantity:
                if tx.type.upper().endswith('BUY'):
                    print('buy:', tx.quantity, tx.id)
                    total_quantity += tx.quantity
                    fifo_amount += tx.price * tx.transaction_metadata['fifo']['quantity']
                elif tx.type.upper().endswith('SELL'):
                    print('sell:', tx.quantity, tx.id)
                    total_quantity -= tx.quantity
                    # fifo_amount -= tx.price * tx.transaction_metadata['fifo']['quantity']
        else:
            if tx.date.year <= date.year and tx.date.month <= date.month:
                if tx.quantity:
                    if tx.type.upper().endswith('BUY'):
                        total_quantity += tx.quantity
                        fifo_amount += tx.price * tx.transaction_metadata['fifo']['quantity']
                    elif tx.type.upper().endswith('SELL'):
                        total_quantity -= tx.quantity
                        # fifo_amount -= tx.price * tx.transaction_metadata['fifo']['quantity']
    
    average_price = 0
    if total_quantity > 0:
        average_price = fifo_amount / total_quantity
    return total_quantity, fifo_amount, average_price



def get_asset_id_by_transaction(db, username):
    transaction = db.query(Transaction).filter(
        Transaction.username == username
    ).all()
    asset = []
    for tx in transaction:
        try:
            if tx.asset_id not in asset:
                asset.append(tx.asset_id)
        except:
            pass
    return asset


def get_account_assets_symbol_by_transaction(db, username):
    transaction = db.query(Transaction).filter(
        Transaction.username == username
    ).all()
    asset = {}
    for tx in transaction:
        if tx.type.upper().endswith('BUY'):
            if tx.asset_id:
                currency = tx.currency
                if currency not in asset:
                    asset[currency] = {}
                if tx.debit_account.name not in asset[currency]:
                    asset[currency][tx.debit_account.name] = []
                if tx.asset.symbol not in asset[currency][tx.debit_account.name]:   
                    asset[currency][tx.debit_account.name].append(tx.asset.symbol)
                # if tx.credit_account.name not in asset:
                #     asset[currency] = {}
                # asset[currency][tx.credit_account.name] = tx.asset.symbol
    return asset

