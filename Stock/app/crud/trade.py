from fastapi import Depends
from sqlalchemy.orm import Session
from app.utils.dependencies import get_db
from sqlalchemy import create_engine
from app.core.config import settings
from app.models.stock import Stocks, InterestStock, AppKey, TradeLog, Nasdaq
from app.schemas import stock as schemas
# from app.schemas import trade as trade_schemas
import json
from sqlalchemy import or_, and_, desc, not_, func, case
from typing import Optional
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from app.utils.trade_log import calculate_capital_gains
from app.crud import stock as stock_crud




# stock code로 가장 최근 거래 내역 조회
def get_latest_trade_by_code(db: Session, username: str, code: str):
    return db.query(TradeLog).filter(
        TradeLog.username == username,
        TradeLog.code == code,
        # TradeLog.price != 0,
        # TradeLog.price != None
    ).order_by(
        desc(TradeLog.date),
        desc(TradeLog.id)
    ).first()

# stock code로 최초 거래 찾기
def get_first_trade_by_code(db: Session, username: str, code: str):
    return db.query(TradeLog).filter(
        TradeLog.username == username,
        TradeLog.code == code
    ).order_by(
        TradeLog.date,
        TradeLog.id
    ).first()

# stock code로 보유수량 0인곳중 가장 최근 거래 내역 조회
def get_latest_trade_by_code_zero_holdings(db: Session, username: str, code: str):
    return db.query(TradeLog).filter(
        TradeLog.username == username,
        TradeLog.code == code,
        TradeLog.holdings_quantity == 0
    ).order_by(
        TradeLog.date,
        TradeLog.id
    ).first()

# stock code로 보유수량 0인곳 이후 첫번째 거래 조회
def get_first_trade_by_code_zero_holdings(db: Session, username: str, code: str):
    # 보유수량이 0인 마지막 거래 날짜 찾기
    zero_holdings_date = db.query(TradeLog.date).filter(
        TradeLog.username == username,
        TradeLog.code == code,
        TradeLog.holdings_quantity == 0
    ).order_by(
        desc(TradeLog.date),
        desc(TradeLog.id)
    ).first()

    if not zero_holdings_date:
        return get_first_trade_by_code(db, username, code)

    # 해당 날짜 이후의 첫 번째 거래 찾기
    return db.query(TradeLog).filter(
        TradeLog.username == username,
        TradeLog.code == code,
        TradeLog.date > zero_holdings_date[0]
    ).order_by(
        TradeLog.date,
        TradeLog.id
    ).first()

# # stock code로 보유수량 0인곳 이후 첫번째 거래 조회
# def get_first_trade_by_code_zero_holdings_id(db: Session, username: str, code: str):
#     # 보유수량이 0인 마지막 거래의 ID 찾기
#     zero_holdings_trade = db.query(TradeLog).filter(
#         TradeLog.username == username,
#         TradeLog.code == code,
#         TradeLog.holdings_quantity == 0
#     ).order_by(
#         desc(TradeLog.date),
#         desc(TradeLog.id)
#     ).first()

#     if not zero_holdings_trade:
#         return get_first_trade_by_code(db, username, code)

#     # 해당 ID 이후의 첫 번째 거래 찾기
#     return db.query(TradeLog).filter(
#         TradeLog.username == username,
#         TradeLog.code == code,
#         TradeLog.id > zero_holdings_trade.id  # date 대신 id로 비교
#     ).order_by(
#         TradeLog.date,
#         TradeLog.id
#     ).first()


# TradeLog 모든 요소 리턴
def get_all_trade_log(db: Session, username: str):
    '''TradeLog 모든 요소 리턴'''
    return db.query(TradeLog).filter(
        TradeLog.username == username
    ).order_by(
        TradeLog.date,
        TradeLog.id
    ).all()

# 자산 리스트 TradeLog.asset_category 첫번째 문자열 리스트 리턴
def get_asset_list(db: Session, username: str):
    '''asset 리스트'''
    trade_log = get_all_trade_log(db, username)
    asset_list = []
    for trade in trade_log:
        asset_list.append(trade.asset_category.split(',')[0])
    return asset_list

# 화폐 리스트 TradeLog.asset_category 마지막 문자열 리스트 리턴
def get_currency_list(db: Session, username: str):
    '''currency 리스트'''
    trade_log = get_all_trade_log(db, username)
    currency_list = []
    for trade in trade_log:
        if trade.asset_category.split(',')[0] == 'exchange':
            currency_list.append(trade.code.lower())
            currency_list.append(trade.name.lower())
    return currency_list

def get_stock_asset_list_by_date(db: Session, username: str):
    return db.query(TradeLog.asset_category).filter(
        ~TradeLog.asset_category.contains('exchange%'),
        ~TradeLog.asset_category.contains('cash%'),
        TradeLog.username == username,
    ).order_by(
        TradeLog.date,
        TradeLog.id
    ).all()


def get_asset_sub_list(db: Session, username: str, asset: str):
    '''asset 하위 리스트'''
    trade_log = get_all_trade_log(db, username)
    asset_sub_list = []
    for trade in trade_log:
        if ',' in trade.asset_category: 
            if trade.asset_category.split(',')[0] == asset:
                asset_sub_list.append(trade.asset_category.split(',')[1])
        else:
            print('자산정보 없음', trade.asset_category)
    return asset_sub_list

def get_asset_filter(db:Session, username:str, asset:str):
    return db.query(TradeLog).filter(
        TradeLog.username == username,
        TradeLog.asset_category.contains(asset)
    ).order_by(
        TradeLog.date,
        TradeLog.id
    ).all()


# 양도소득 계산
def get_trades_for_tax(db: Session, username: str, code: str, year: int):
    trades = db.query(TradeLog).filter(
        TradeLog.username == username,
        TradeLog.code == code,
        TradeLog.date <= f"{year}-12-31"
    ).order_by(
        TradeLog.date,
        TradeLog.id
    ).all()
    
    buy_queue = []
    tax_results = {
        'capital_gains': [],  # 매도 시 양도소득 계산 결과
        'current_holdings': []  # 현재 보유 내역
    }
    
    for trade in trades:
        if trade.action == 'in':
            buy_queue.append({
                'quantity': trade.quantity,
                'price': trade.price,
                'date': trade.date,
                'fee': trade.fee
            })
        elif trade.action == 'out':
            # 매도 시 FIFO로 매수 내역과 매칭
            remaining_quantity = abs(trade.quantity)
            while remaining_quantity > 0 and buy_queue:
                oldest_buy = buy_queue[0]
                matched_quantity = min(remaining_quantity, oldest_buy['quantity'])
                
                gain = {
                    'quantity': matched_quantity,
                    'buy_price': oldest_buy['price'],
                    'buy_date': oldest_buy['date'],
                    'buy_fee': abs(oldest_buy['fee']),  # 절대값으로 변환
                    'sell_price': trade.price,
                    'sell_date': trade.date,
                    'sell_fee': abs(trade.fee),  # 절대값으로 변환
                    'sell_tax': abs(trade.tax),  # 절대값으로 변환
                    'holding_days': (trade.date - oldest_buy['date']).days,
                    # 추가 계산 정보
                    'buy_amount': matched_quantity * oldest_buy['price'],
                    'sell_amount': matched_quantity * trade.price,
                    'total_fee': abs(oldest_buy['fee']) + abs(trade.fee) + abs(trade.tax)
                }
                tax_results['capital_gains'].append(gain)
                
                remaining_quantity -= matched_quantity
                oldest_buy['quantity'] -= matched_quantity
                
                if oldest_buy['quantity'] == 0:
                    buy_queue.pop(0)
    
    # 현재 보유 내역 추가
    for holding in buy_queue:
        tax_results['current_holdings'].append({
            'quantity': holding['quantity'],
            'price': holding['price'],
            'date': holding['date'],
            'fee': holding['fee']
        })
    
    return tax_results



# 현재 보유 수량 계산
def get_holdings(db: Session, username: str, code: str):
    # 전체 기간의 순매수량 계산
    return db.query(
        func.sum(
            case((TradeLog.action == 'in', TradeLog.quantity), else_=TradeLog.quantity)
        )
    ).filter(
        TradeLog.username == username,
        TradeLog.code == code
    ).scalar() or 0



# 특정 날짜 이전의 보유수량 계산
def get_holdings_before_date(db: Session, username: str, code: str, date: date):
    """특정 날짜 이전의 보유수량 계산"""
    return db.query(
        func.sum(
            case((TradeLog.action == 'in', TradeLog.quantity), else_=-TradeLog.quantity)
        )
    ).filter(
        TradeLog.username == username,
        TradeLog.code == code,
        TradeLog.date < date
    ).scalar() or 0



# 보유수량과 평균단가 계산
def calculate_holdings(db: Session, trade_log: schemas.Trade) -> tuple[Decimal, Decimal]:
    """보유수량과 평균단가 계산"""
    previous_trades = db.query(TradeLog).filter(
        TradeLog.username == trade_log.username,
        TradeLog.code == trade_log.code,
        TradeLog.date < trade_log.date
    ).order_by(TradeLog.date, TradeLog.id).all()
    
    current_holdings = Decimal(0)
    total_cost = Decimal(0)
    PRICE_PRECISION = Decimal('0.0000000001')
    
    if previous_trades:
        last_trade = previous_trades[-1]
        current_holdings = last_trade.holdings_quantity if last_trade.holdings_quantity is not None else Decimal(0)
        if current_holdings > 0 and last_trade.purchases_price:
            total_cost = current_holdings * last_trade.purchases_price
    
    if trade_log.action == 'in':
        total_cost += trade_log.price * trade_log.quantity
        current_holdings += trade_log.quantity
    else:
        if current_holdings > 0:
            current_holdings += trade_log.quantity
    
    purchases_price = (total_cost / current_holdings).quantize(PRICE_PRECISION, rounding=ROUND_HALF_UP) if current_holdings > 0 else Decimal(0)
    
    db_trade = TradeLog(
                        date=trade_log.date,
                        asset_category=trade_log.asset_category,
                        market=trade_log.market,
                        code=trade_log.code,
                        name=trade_log.name,
                        price=trade_log.price,
                        quantity=trade_log.quantity,
                        amount=trade_log.amount,
                        action=trade_log.action,
                        username=trade_log.username,
                        memo=trade_log.memo,
                        fee=trade_log.fee,
                        tax=trade_log.tax,
                        holdings_quantity=current_holdings,
                        purchases_price=purchases_price,
                        # balance=trade_log.balance
                    )
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    
    return db_trade
    



def update_trade_and_recalculate(db: Session, trade_update: schemas.TradeItem):
    trade = db.query(TradeLog).filter(TradeLog.id == trade_update.id).first()
    old_date = trade.date
    
    # SQLAlchemy 모델의 경우 __dict__ 사용
    for key, value in trade_update.__dict__.items():
        if not key.startswith('_') and value is not None:  # SQLAlchemy 내부 속성 제외
            setattr(trade, key, value)
    
    affected_trades = db.query(TradeLog).filter(
        TradeLog.username == trade.username,
        TradeLog.code == trade.code,
        TradeLog.date >= min(old_date, trade_update.date)
    ).order_by(TradeLog.date, TradeLog.id).all()
    
    current_holdings = Decimal(0)
    total_cost = Decimal(0)
    PRICE_PRECISION = Decimal('0.0001')  # 소수점 4자리
    
    for t in affected_trades:
        if t.quantity is None or t.quantity == 0:  # 배당금 등의 경우
            t.quantity = Decimal(0)
            t.holdings_quantity = current_holdings
            t.purchases_price = (total_cost / current_holdings).quantize(PRICE_PRECISION, rounding=ROUND_HALF_UP) if current_holdings > 0 else Decimal(0)
        else:
            if t.action == 'in':
                total_cost += t.price * t.quantity
                current_holdings += t.quantity
            else:
                if current_holdings > 0:
                    avg_price = (total_cost / current_holdings).quantize(PRICE_PRECISION, rounding=ROUND_HALF_UP)
                    total_cost = avg_price * (current_holdings + t.quantity)
                current_holdings += t.quantity
            
            t.holdings_quantity = current_holdings
            t.purchases_price = (total_cost / current_holdings).quantize(PRICE_PRECISION, rounding=ROUND_HALF_UP) if current_holdings > 0 else Decimal(0)

        print(f'날짜: {t.date}, ID: {t.id}, 수량: {t.quantity}, '
              f'보유량: {t.holdings_quantity}, 평균단가: {t.purchases_price}')

    db.commit()
    return trade






