from fastapi import Depends
from sqlalchemy.orm import Session
from app.utils.dependencies import get_db
from sqlalchemy import create_engine
from app.core.config import settings
from app.models.stock import Stocks, InterestStock, AppKey, TradeLog, Nasdaq, Amex, Nyse
from app.schemas import stock as schemas
from app.crud import trade as trade_crud
# from app.schemas import trade as trade_schemas
import json
from sqlalchemy import or_, and_, desc, not_, func, case
from typing import Optional
from datetime import date
from decimal import Decimal, ROUND_HALF_UP


# Symbol 이 nasdaq, amex, nyse 중 어디에 있는지 확인
def check_symbol_nasdaq(db: Session, symbol: str):
    return db.query(Nasdaq).filter(Nasdaq.Symbol == symbol).first()

# Symbol 이 nasdaq, amex, nyse 중 어디에 있는지 확인
def check_symbol_amex(db: Session, symbol: str):
    return db.query(Amex).filter(Amex.Symbol == symbol).first()

# Symbol 이 nasdaq, amex, nyse 중 어디에 있는지 확인
def check_symbol_nyse(db: Session, symbol: str):
    return db.query(Nyse).filter(Nyse.Symbol == symbol).first()

# 종목코드로 주식 조회
def get_stock_by_code(db: Session, code: str):
    return db.query(Stocks).filter(Stocks.shcode == code).first()

# 사용자별 관심종목 불러오기
def get_interest_stock_by_username(db: Session, username: str):
    return db.query(InterestStock).filter(
        InterestStock.username == username
    ).all()


# 관심종목 불러오기 (사용자별)
def get_interest_stocks(db: Session, interest_stock: schemas.InterestStock):
    return db.query(InterestStock).filter(
        InterestStock.username == interest_stock.username
    ).all()

# 존재 유무 확인 (사용자별)
def get_interest_stock(db: Session, interest_stock: schemas.InterestStock):
    stock = db.query(InterestStock).filter(
        InterestStock.종목코드 == interest_stock.종목코드,
        InterestStock.username == interest_stock.username
    ).first()
    # print('stock:', stock)
    return stock

# 관심종목 추가
def insert_interest_stock(db: Session, interest_stock: schemas.InterestStock):
    db_stock = InterestStock(
        종목코드=interest_stock.종목코드, 
        한글기업명=interest_stock.한글기업명, 
        시장구분=interest_stock.시장구분, 
        업종구분명=interest_stock.업종구분명,
        username=interest_stock.username  # 사용자 ID 추가
    )
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return get_interest_stock(db, interest_stock)

# 관심종목 삭제
def delete_interest_stock(db: Session, interest_stock: schemas.InterestStock):
    db.query(InterestStock).filter(
        InterestStock.종목코드 == interest_stock.종목코드,
        InterestStock.username == interest_stock.username
    ).delete()
    db.commit()

# tag 업데이트 (사용자별)
def update_interest_stock_tag(db: Session, stock: schemas.InterestStockTag):
    stock_instance = db.query(InterestStock).filter(
        InterestStock.종목코드 == stock.종목코드,
        InterestStock.username == stock.username
    ).first()
    if stock_instance:
        stock_instance.tag = stock.tag
        db.commit()
        db.refresh(stock_instance)
    return stock_instance



def insert_stocks(db: Session, stocks: dict):
    # 인스턴스 생성
    stock_instance = Stocks(
        shcode=stocks['단축코드'], 
        shname=stocks['종목명'], 
        gubun=stocks['구분(1:코스피2:코스닥)'], 
        ETFgubun=stocks['ETF구분(1:ETF)']
    )
    # DB에 추가
    db.add(stock_instance)
    db.commit()
    db.refresh(stock_instance)  # Stocks 클래스 대신 인스턴스를 전달
    return stock_instance

def get_stocks(db: Session, gubun: str):
    return db.query(Stocks).filter(Stocks.gubun == gubun).all()

# 주식 shcode 있는지 확인
def check_stock_shcode(db: Session, shcode: str):
    return db.query(Stocks).filter(Stocks.shcode == shcode).first()

# 주식 shname 있는지 확인
def check_stock_shname(db: Session, shname: str):
    return db.query(Stocks).filter(Stocks.shname == shname).first()

# 주식 코드로 검색
def search_stock_shcode(db: Session, shcode: str):
    return db.query(Stocks).filter(Stocks.shcode == shcode).first()

# 주식 종목명으로 검색
def search_stock_shname(db: Session, shname: str):
    return db.query(Stocks).filter(Stocks.shname == shname).first()

def search_stocks(db: Session, query: str):
    """
    종목코드 또는 기업명으로 주식 검색
    """
    return db.query(Stocks).filter(
        or_(
            Stocks.shcode.contains(query),
            Stocks.shname.contains(query)
        )
    ).all() 

# NASDAQ 종목명으로 검색
def search_stocks_nasdaq(db: Session, query: str):
    # print('query:', query)
    return db.query(Nasdaq).filter(
        Nasdaq.Symbol.contains(query)
        
    ).all()

# 앱키 조회
def get_app_key(db: Session, app_key: schemas.AppKeyRequest):
    return db.query(AppKey).filter(
        AppKey.username == app_key.username,
        AppKey.cname == app_key.cname
    ).first()
# 앱키 삭제
def delete_app_key(db: Session, app_key: schemas.AppKeyRequest):
    db.query(AppKey).filter(
            AppKey.username == app_key.username,
            AppKey.cname == app_key.cname
            ).delete()
    db.commit()

# 앱키 추가 (앱키 중복 방지)
def insert_app_key(db: Session, app_key: schemas.AppKey):
    if get_app_key(db, app_key):
        delete_app_key(db, app_key)
    db_app_key = AppKey(
        appkey=app_key.appkey,
        appsecretkey=app_key.appsecretkey,
        cname=app_key.cname,
        username=app_key.username
    )
    db.add(db_app_key)
    db.commit()
    db.refresh(db_app_key)
    return db_app_key




# 주식 거래 현금 환전 로그 조회
def get_trade_exchange(db: Session, trade_log: schemas.Trade):
    return db.query(trade_log).and_(
        trade_log.asset_category != 'cash',
        trade_log.market == 'exchange',
        trade_log.username == trade_log.username
    ).first()

# 주식 거래 로그 조회
def get_trade(db: Session, trade_log: schemas.Trade):
    return db.query(trade_log).and_(
        trade_log.asset_category != 'cash',
        trade_log.market != 'exchange',
        trade_log.username == trade_log.username
    ).first()

# 현금 입출금 로그 조회
def get_transaction(db: Session, transaction_log : schemas.Transaction):
    return db.query(transaction_log).and_(
        transaction_log.asset_category == 'cash',
        transaction_log.username == transaction_log.username
    ).first()

# 환전 로그 조회
def get_exchange(db: Session, exchange_log: schemas.Exchange):
    return db.query(exchange_log).and_(
        exchange_log.asset_category == 'exchange',
        exchange_log.username == exchange_log.username
    ).first()

# 배당금 수령 로그 조회
def get_dividend(db: Session, dividend_log: schemas.Dividend):
    return db.query(dividend_log).and_(
        dividend_log.asset_category == 'dividend',
        dividend_log.username == dividend_log.username
    ).first()

def insert_dividend(db: Session, dividend_log: schemas.Dividend):
    db_dividend = TradeLog(
        date=dividend_log.date,
        asset_category=dividend_log.asset_category,
        market=dividend_log.market,
        code=dividend_log.code,
        name=dividend_log.name,
        amount=dividend_log.amount,
        fee=dividend_log.fee,
        tax=dividend_log.tax,
        action=dividend_log.action,
        username=dividend_log.username,
        memo=dividend_log.memo,
    )
    db.add(db_dividend)
    db.commit()
    db.refresh(db_dividend)
    return db_dividend

# 주식 거래 로그 추가
from decimal import Decimal, ROUND_HALF_UP



# 현금 입출금 로그 추가
def insert_transaction(db: Session, transaction_log: schemas.Transaction):
    db_transaction = TradeLog(
        date=transaction_log.date,
        asset_category=transaction_log.asset_category,
        code=transaction_log.code,
        name=transaction_log.name,
        amount=transaction_log.amount,
        action=transaction_log.action,
        username=transaction_log.username,
        memo=transaction_log.memo,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

# 환전 로그 추가
def insert_exchange(db: Session, exchange_log: schemas.Exchange):
    db_exchange_log = TradeLog(
        date=exchange_log.date,
        asset_category=exchange_log.asset_category,
        name=exchange_log.name,
        code=exchange_log.code,
        quantity=exchange_log.quantity,
        price=exchange_log.price,
        amount=exchange_log.amount,
        action=exchange_log.action,
        username=exchange_log.username,
        memo=exchange_log.memo,
    )
    db.add(db_exchange_log)
    db.commit()
    db.refresh(db_exchange_log)
    return db_exchange_log


# id로 주식 거래 현금 환전 로그 조회
def get_trade_by_id(db: Session, trade_log: schemas.Trade):
    return db.query(TradeLog).filter(
        TradeLog.id == trade_log.id,
        TradeLog.username == trade_log.username
    ).first()


# id로 주식 거래 로그 삭제
def delete_trade(db: Session, trade_log: schemas.Trade):
    db.query(TradeLog).filter(
        TradeLog.id == trade_log.id,
        TradeLog.username == trade_log.username
    ).delete()
    db.commit()
    
# 모두 불러오기
def get_all_trade(db: Session, username: str):
    # 최신순 정렬
    return db.query(TradeLog).filter(
        TradeLog.username == username
    ).order_by(TradeLog.date.desc()).all()
    
# id로 주식 거래 로그 삭제
def delete_trade_by_id(db: Session, trade_log: schemas.Trade):
    db.query(TradeLog).filter(
        TradeLog.id == trade_log.id,
        TradeLog.username == trade_log.username
    ).delete()
    db.commit()
    
# id로 주식 거래 로그 조회
def get_trade_by_id(db: Session, trade_log: schemas.DeleteTrade):
    return db.query(TradeLog).filter(
        TradeLog.id == trade_log.id,
        TradeLog.username == trade_log.username
    ).first()

# id로 주식 거래 로그 수정
def update_trade_by_id(db: Session, trade_log: schemas.TradeItem):
    trade_instance = db.query(TradeLog).filter(
        TradeLog.id == trade_log.id,
        TradeLog.username == trade_log.username
    ).first()
    
    if trade_instance:
        # 업데이트할 데이터 준비
        update_data = {
            'date': trade_log.date,
            'asset_category': trade_log.asset_category,
            'market': trade_log.market,
            'code': trade_log.code,
            'name': trade_log.name,
            'price': trade_log.price,
            'quantity': trade_log.quantity,
            'amount': trade_log.amount,
            'fee': trade_log.fee,
            'tax': trade_log.tax,
            'action': trade_log.action,
            'memo': trade_log.memo
        }
        
        # 데이터 업데이트
        for key, value in update_data.items():
            setattr(trade_instance, key, value)
            
        db.commit()
        db.refresh(trade_instance)
        
    return trade_instance


def get_trade_logs_pagination(
        db: Session,
        username: str,
        skip: int = 0,
        limit: int = 10,
        code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        asset_category: Optional[str] = None
    ):
    
    # 서브 리스트 만들기
    asset = (asset_category + ',').split(',')[0]
    print('asset:', asset)
    currency_list = trade_crud.get_currency_list(db, username)
    print('currency_list:', currency_list)
    sub = asset_category.replace(asset, '').strip(',')
    for currency in currency_list:
        sub = sub.replace(currency, '').strip(',')
    # print('sub:', sub)
    sub_list = sub.split(',')
    print('sub_list:', sub_list)
    currency = asset_category.split(',')[-1] 
    currency = currency if currency in currency_list else ''
    print('currency:', currency)
    # 기본 쿼리 생성
    query = db.query(TradeLog)
    
    
    # 필터 조건 추가
    conditions = []
    if username:
        conditions.append(TradeLog.username == username)
    if code:
        conditions.append(TradeLog.code == code)
    if start_date:
        conditions.append(TradeLog.date >= start_date)
    if end_date:
        conditions.append(TradeLog.date <= end_date)
    if asset_category:
        conditions.append(TradeLog.asset_category.like(asset + '%'))
        sub_conditions = []
        for sub in sub_list:
            if sub:
                sub_conditions.append(TradeLog.asset_category.like('%' + sub + '%'))
        conditions.append(or_(*sub_conditions))
        if currency:
            conditions.append(TradeLog.asset_category.like('%' + currency + '%'))
        # if asset_category == 'stock':
        #     conditions.append(not_(TradeLog.asset_category.like('cash%')))
        #     conditions.append(not_(TradeLog.asset_category.like('exchange%')))
        # else:
        #     conditions.append(TradeLog.asset_category.like(asset_category + '%'))
    
    if conditions:
        query = query.filter(and_(*conditions))
    
    # 전체 아이템 수 계산
    total = query.count()
    
    # 정렬 및 페이지네이션 적용
    items = query.order_by(desc(TradeLog.date), desc(TradeLog.id))\
                .offset(skip)\
                .limit(limit)\
                .all()
    
    # trade_asset_category = query.with_entities(TradeLog.asset_category).distinct().all()
    # print('trade_asset_category:', trade_asset_category)
    
    return {
        "total": total,
        "items": items,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit,
        "has_next": skip + limit < total,
        "has_prev": skip > 0,
        # "trade_asset_category": [asset_category for asset_category, in trade_asset_category]
    }

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

# 새로운 거래 생성 시 보유수량과 평균단가 계산
def calculate_holdings_for_insert(db: Session, trade_log: schemas.Trade):
    previous_trades = db.query(TradeLog).filter(
        TradeLog.username == trade_log.username,
        TradeLog.code == trade_log.code,
        TradeLog.date <= trade_log.date
    ).order_by(TradeLog.date, TradeLog.id).all()
    
    current_holdings = Decimal(0)
    total_cost = Decimal(0)
    PRICE_PRECISION = Decimal('0.0001')  # 소수점 4자리
    
    # 이전 거래들 계산
    for t in previous_trades:
        if t.quantity is None:
            t.quantity = Decimal(0)
        
        if t.action == 'in':
            total_cost += t.price * t.quantity
            current_holdings += t.quantity
        else:
            if current_holdings > 0:
                avg_price = (total_cost / current_holdings).quantize(PRICE_PRECISION, rounding=ROUND_HALF_UP)
                total_cost = avg_price * (current_holdings + t.quantity)
            current_holdings += t.quantity
    
    # 새 거래 생성
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
        tax=trade_log.tax
    )
    
    # 새 거래의 보유수량과 평균단가 계산
    if trade_log.action == 'in':
        total_cost += trade_log.price * trade_log.quantity
        current_holdings += trade_log.quantity
    else:
        if current_holdings > 0:
            avg_price = (total_cost / current_holdings).quantize(PRICE_PRECISION, rounding=ROUND_HALF_UP)
            total_cost = avg_price * (current_holdings + trade_log.quantity)
        current_holdings += trade_log.quantity
    
    db_trade.holdings_quantity = current_holdings
    db_trade.purchases_price = (total_cost / current_holdings).quantize(PRICE_PRECISION, rounding=ROUND_HALF_UP) if current_holdings > 0 else Decimal(0)
    
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    
    print(f'새 거래 - 날짜: {db_trade.date}, 수량: {db_trade.quantity}, '
          f'보유량: {db_trade.holdings_quantity}, 평균단가: {db_trade.purchases_price}')
    
    return db_trade


# 거래 수정 및 보유 수량 재계산
def update_trade_and_recalculate(db: Session, trade_update: schemas.TradeItem):
    trade = db.query(TradeLog).filter(TradeLog.id == trade_update.id).first()
    old_date = trade.date
    
    for key, value in trade_update.dict(exclude_unset=True).items():
        setattr(trade, key, value)
    
    affected_trades = db.query(TradeLog).filter(
        TradeLog.username == trade.username,
        TradeLog.code == trade.code,
        TradeLog.date >= min(old_date, trade_update.date)
    ).order_by(TradeLog.date, TradeLog.id).all()
    
    current_holdings = Decimal(0)
    total_cost = Decimal(0)
    PRICE_PRECISION = Decimal('0.0001')
    last_valid_price = Decimal(0)  # 마지막 유효한 평균단가 저장
    
    for t in affected_trades:
        # 이전 거래의 평균단가 저장
        if t.purchases_price and t.purchases_price > 0:
            last_valid_price = t.purchases_price

        if t.quantity is None or t.quantity == 0:  # 배당금 등의 경우
            t.quantity = Decimal(0)
            t.holdings_quantity = current_holdings
            # 배당 시에는 이전 평균단가 유지
            t.purchases_price = last_valid_price if current_holdings > 0 else Decimal(0)
            continue
            
        if t.action == 'in':
            # 매수 시: (기존 총액 + 매수금액) / (기존 수량 + 매수수량)
            total_cost += t.price * t.quantity
            current_holdings += t.quantity
            if current_holdings > 0:
                t.purchases_price = (total_cost / current_holdings).quantize(PRICE_PRECISION, rounding=ROUND_HALF_UP)
                last_valid_price = t.purchases_price
        else:
            # 매도 시: 보유수량만 감소 (평균단가 유지)
            current_holdings += t.quantity  # 음수값이므로 실제로는 감소
            if current_holdings > 0:
                t.purchases_price = last_valid_price
                total_cost = current_holdings * last_valid_price
            else:
                total_cost = Decimal(0)
                t.purchases_price = Decimal(0)
                last_valid_price = Decimal(0)
        
        t.holdings_quantity = current_holdings
        
        print(f'날짜: {t.date}, ID: {t.id}, 액션: {t.action}, '
              f'수량: {t.quantity}, 보유량: {t.holdings_quantity}, '
              f'평균단가: {t.purchases_price}, 총액: {total_cost}')

    db.commit()
    return trade

def update_trade_and_feeTax_recalculate(db: Session, trade_update: schemas.TradeItem):
    trade = db.query(TradeLog).filter(TradeLog.id == trade_update.id).first()
    old_date = trade.date
    
    for key, value in trade_update.dict(exclude_unset=True).items():
        setattr(trade, key, value)
    
    affected_trades = db.query(TradeLog).filter(
        TradeLog.username == trade.username,
        TradeLog.code == trade.code,
        TradeLog.date >= min(old_date, trade_update.date)
    ).order_by(TradeLog.date, TradeLog.id).all()
    
    current_holdings = Decimal(0)
    total_cost = Decimal(0)
    PRICE_PRECISION = Decimal('0.0001')
    
    for t in affected_trades:
        if t.quantity is None or t.quantity == 0:  # 배당금 등의 경우
            t.quantity = Decimal(0)
            t.holdings_quantity = current_holdings
            t.purchases_price = (total_cost / current_holdings).quantize(PRICE_PRECISION, rounding=ROUND_HALF_UP) if current_holdings > 0 else Decimal(0)
        else:
            if t.action == 'in':
                # 매수 시: 매수금액 + 수수료
                trade_cost = (t.price * t.quantity) + abs(t.fee or Decimal(0))
                total_cost += trade_cost
                current_holdings += t.quantity
            else:
                # 매도 시: 평균단가로 보유금액 감소, 수수료와 세금은 고려하지 않음
                if current_holdings > 0:
                    avg_price = (total_cost / current_holdings).quantize(PRICE_PRECISION, rounding=ROUND_HALF_UP)
                    total_cost = avg_price * (current_holdings + t.quantity)
                current_holdings += t.quantity
            
            t.holdings_quantity = current_holdings
            # 평균단가 계산 (총비용 / 보유수량)
            t.purchases_price = (total_cost / current_holdings).quantize(PRICE_PRECISION, rounding=ROUND_HALF_UP) if current_holdings > 0 else Decimal(0)

        print(f'날짜: {t.date}, ID: {t.id}, 수량: {t.quantity}, '
              f'보유량: {t.holdings_quantity}, 평균단가: {t.purchases_price}, '
              f'총비용: {total_cost}')

    db.commit()
    return trade


def calculate_feeTax_holdings_for_insert(db: Session, trade_log: schemas.Trade):
    previous_trades = db.query(TradeLog).filter(
        TradeLog.username == trade_log.username,
        TradeLog.code == trade_log.code,
        TradeLog.date <= trade_log.date
    ).order_by(TradeLog.date, TradeLog.id).all()
    
    current_holdings = Decimal(0)
    total_cost = Decimal(0)
    PRICE_PRECISION = Decimal('0.0001')
    
    # 이전 거래들 계산
    for t in previous_trades:
        if t.quantity is None:
            t.quantity = Decimal(0)
        
        if t.action == 'in':
            # 매수 시: 매수금액 + 수수료
            trade_cost = (t.price * t.quantity) + abs(t.fee or Decimal(0))
            total_cost += trade_cost
            current_holdings += t.quantity
        else:
            if current_holdings > 0:
                avg_price = (total_cost / current_holdings).quantize(PRICE_PRECISION, rounding=ROUND_HALF_UP)
                total_cost = avg_price * (current_holdings + t.quantity)
            current_holdings += t.quantity
    
    # 새 거래 생성
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
        tax=trade_log.tax
    )
    
    # 새 거래의 보유수량과 평균단가 계산
    if trade_log.action == 'in':
        # 매수 시: 매수금액 + 수수료
        trade_cost = (trade_log.price * trade_log.quantity) + abs(trade_log.fee or Decimal(0))
        total_cost += trade_cost
        current_holdings += trade_log.quantity
    else:
        if current_holdings > 0:
            avg_price = (total_cost / current_holdings).quantize(PRICE_PRECISION, rounding=ROUND_HALF_UP)
            total_cost = avg_price * (current_holdings + trade_log.quantity)
        current_holdings += trade_log.quantity
    
    db_trade.holdings_quantity = current_holdings
    db_trade.purchases_price = (total_cost / current_holdings).quantize(PRICE_PRECISION, rounding=ROUND_HALF_UP) if current_holdings > 0 else Decimal(0)
    
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    
    print(f'새 거래 - 날짜: {db_trade.date}, 수량: {db_trade.quantity}, '
          f'보유량: {db_trade.holdings_quantity}, 평균단가: {db_trade.purchases_price}, '
          f'총비용: {total_cost}')
    
    return db_trade