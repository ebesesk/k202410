from fastapi import APIRouter, Depends, HTTPException, Header, Query
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session  # 상단에 추가
from app.crud import stock as crud
from app.crud import trade as trade_crud
from app.schemas import stock as schemas
from app.utils.dependencies import get_db, get_current_user
from app.utils.trade_log import get_trade_logs_pagination, sign_trade_value, get_trade_log_fee_tax, get_asset_summary, format_string
from app.core.config import settings
from pprint import pprint
from decimal import Decimal
from math import trunc
from app.utils.fdr_util import get_fdr_price
COMMISSION_RATE_STOCK_KR = Decimal(settings.COMMISSION_RATE_STOCK_KR)  # 증권 수수료
TAX_RATE_STOCK_KR = Decimal(settings.TAX_RATE_STOCK_KR)  # 증권 세금
DIVIDEND_TAX_RATE_STOCK_KR = Decimal(settings.DIVIDEND_TAX_RATE_STOCK_KR)  # 배당 소득세
COMMISSION_RATE_STOCK_US = Decimal(settings.COMMISSION_RATE_STOCK_US)  # 해외 수수료
INTERNATIONAL_TRANSACTION_FEES = Decimal(settings.INTERNATIONAL_TRANSACTION_FEES)  # 해외 주식 수수료


router = APIRouter()

# POST ##############################################

@router.post("/trade_log")
async def insert_trade_log(
        trade: schemas.Trade,
        key: str = Header(None, alias="X-API-KEY"),
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):
    '''
    주식 거래 로그 제공 API
    '''
    trade = get_trade_log_fee_tax(trade)
    trade.asset_category = format_string(trade.asset_category)
    print('trade:', trade)
            
    trade.username = current_user['username']
    # 대문자로 변환     
    trade.market = trade.market.upper()
    trade.asset_category = trade.asset_category.lower()
    trade.code = trade.code.upper()
    
    # print('get_trade_log:', trade)
    # print('trade.action:', trade.action)
    # print(trade.action)
    trade = sign_trade_value(trade)
    # print('trade:', trade)
    # trade_crud.calculate_holdings_for_insert(db, trade)
    trade_crud.calculate_holdings(db, trade)
    # trade.holdings_quantity = holdings_quantity
    # trade.purchases_price = purchases_price
    # trade_crud.create_trade_db(db, trade)
    
    zero_holdings = trade_crud.get_first_trade_by_code(db, trade.username, trade.code)
    if zero_holdings:
        trade_crud.update_trade_and_recalculate(db, zero_holdings)
    
    return {"message": "주식 거래 로그 제공 API"}

@router.post("/dividend_log")
async def insert_dividend_log(
    dividend_log: schemas.Dividend,
    key: str = Header(None, alias="X-API-KEY"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    '''
    배당금 수령 로그 제공 API
    '''
    username = current_user['username']
    dividend_log.username = username
    dividend_log.market = dividend_log.market.upper()
    dividend_log.asset_category = dividend_log.asset_category.lower()
    dividend_log.code = dividend_log.code.upper()
    print('dividend_log:', dividend_log)
    dividend_log = get_trade_log_fee_tax(dividend_log)
    dividend_log = sign_trade_value(dividend_log)
    crud.insert_dividend(db, dividend_log)
    return {"message": "배당금 수령 로그 제공 API"}

@router.post("/transaction_log")
async def insert_transaction_log(
        transaction_cash: schemas.Transaction,
        key: str = Header(None, alias="X-API-KEY"),
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):
    '''
    현금 입출금 로그 제공 API
    '''
    print('transaction_cash:', transaction_cash)

    transaction_cash.username = current_user['username']
    transaction_cash.asset_category = transaction_cash.asset_category.lower()
    transaction_cash.code = transaction_cash.code.upper()
    
    if transaction_cash.action == 'in':
        transaction_cash.amount = transaction_cash.amount * 1
    elif transaction_cash.action == 'out':
        transaction_cash.amount = transaction_cash.amount * -1
    
    print('get_transaction_log:', transaction_cash)
    crud.insert_transaction(db, transaction_cash)
    return {"message": "현금 입출금 로그 제공 API"}

@router.post("/exchange_log")
async def insert_exchange_log(
    exchange_log: schemas.Exchange,
    key: str = Header(None, alias="X-API-KEY"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    '''
    외환 환전 로그 제공 API
    '''
    username = current_user['username']
    exchange_log.username = username
    print('get_exchange_log:', exchange_log)
    exchange_log.asset_category = exchange_log.asset_category.lower()
    exchange_log.code = exchange_log.code.upper()   # 환전받을 통화
    exchange_log.name = exchange_log.name.upper()   # 환전할 통화
    
    if exchange_log.action == 'in':
        exchange_log.quantity = trunc(abs(exchange_log.quantity))
        exchange_log.amount = trunc(abs(exchange_log.amount)) * -1
    elif exchange_log.action == 'out':
        exchange_log.quantity = trunc(abs(exchange_log.quantity)) * -1
        exchange_log.amount = trunc(abs(exchange_log.amount))
    
    crud.insert_exchange(db, exchange_log)
    return {"message": "외환 환전 로그 제공 API"}



   
@router.delete("/trade_log")
def delete_trade_log(
    trade_log: schemas.DeleteTrade,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    trade_log.username = current_user['username']
    # 있는지 확인
    trade_log_exist = crud.get_trade_by_id(db, trade_log)
    if trade_log_exist:
        crud.delete_trade_by_id(db, trade_log)
        return {"message": "주식 거래 로그 삭제 API"}
    else:
        return {"message": "주식 거래 로그 없음"}
    
@router.put("/trade_log")
def update_trade_log(
        trade_log: schemas.TradeItem,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):
    print('update_trade_log:', trade_log)
    print('id:', trade_log.id)
    
    trade_log.username = current_user['username']
    # 존재 여부 확인
    trade_log_exist = crud.get_trade_by_id(db, trade_log)
    if trade_log_exist:
        
        trade_log = get_trade_log_fee_tax(trade_log)
        trade_log = sign_trade_value(trade_log) # 거래 로그 값 부호 변경
        
        category = trade_log.asset_category
        if 'stock' in category:
            holdings = trade_crud.update_trade_and_recalculate(db, trade_log)
            print('holdings:', holdings)
            trade_log.holdings_quantity = holdings
        else:
            crud.update_trade_by_id(db, trade_log)
        
    else:
        raise HTTPException(status_code=404, detail="주식 거래 로그 없음")
    return {"message": "주식 거래 로그 수정 API"}



# GET ##############################################

@router.get("/trades/all_tags")
def read_all_tags(
    key: str = Header(None, alias="X-API-KEY"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)    
):
    username = current_user['username']
    # TradeLog 테이블 조회
    trade_log = crud.get_all_trade(db, username)    
    
    trade_name = []
    asset_categories = ['cash', 'exchange']
    asset_categories_sub = []
    
    asset_list = ['cash', 'exchange']
    currencies = []
    trade_market = []
    cashes = []
    exchange_name = ['KRW', 'USD']
    exchange_code = ['KRW', 'USD']
    for log in trade_log:
        # print('log:', log.__dict__)
        category = format_string(log.asset_category)

        asset_categories.append(category.split(',')[0])
        asset_categories.append(category)
        if category.split(',')[0] not in asset_list:
            asset_list.append(category.split(',')[0])
        # print('asset_list:', asset_list)
        
        
        
        
        if 'cash' not in log.asset_category and 'exchange' not in log.asset_category:
            trade_market.append(log.market)
            # 주식 종목 이름과 코드 중복 검사
            # if len(log.asset_category.split(',')) > 2:
            #     log.asset_category = log.asset_category.split(',')[0] + ',' + log.asset_category.split(',')[1]
            if {'name': log.name, 'code': log.code, 'market': log.market,'asset_category': log.asset_category} not in trade_name and len(log.asset_category.split(','))<3:
                trade_name.append({'name': log.name, 'code': log.code, 'market': log.market, 'asset_category': log.asset_category}) 
        if 'cash' in log.asset_category:
            # cashs.append(log.code)
            # print('cashs:', log)
            if {'name': log.name, 'code': log.code, 'asset_category': log.asset_category} not in cashes:
                cashes.append({'name': log.name, 'code': log.code, 'asset_category': log.asset_category})
        if 'exchange' in log.asset_category:
            exchange_name.append(log.name)
            exchange_code.append(log.code)
        if len(category.split(',')) > 1:
            currencies.append(category.split(',')[-1])
    
    # 자산 카테고리 cash, exchange, stock.. asset_categories_obj 생성
    asset_categories_obj = {}
    for asset in asset_list:
        _sub_list = []
        _currency = []
        for log in trade_log:
            if asset in log.asset_category:
                if ',' in log.asset_category:
                    currency = log.asset_category.split(',')[-1]
                    if currency not in _currency:
                        _currency.append(currency)
                if 'exchange' in log.asset_category:
                    currency = log.name.lower()
                    currency2 = log.code.lower()
                    if currency not in _currency:
                        _currency.append(currency)
                    if currency2 not in _currency:
                        _currency.append(currency2)
                # else:
                #     currency = asset.split(',')[-1]
                if ',' in log.asset_category:
                    _sub = log.asset_category.split(',')[1]
                else:
                    continue
                    _sub = log.asset_category
                # 중복 검사
                if _sub not in _sub_list and _sub not in currencies:
                    _sub_list.append(_sub)
                
        # print('asset:', asset, '_sub_list:', _sub_list)
        asset_categories_obj[asset] = {}
        asset_categories_obj[asset]['sub'] = _sub_list
        asset_categories_obj[asset]['currency'] = _currency
    # print('asset_categories_obj:', asset_categories_obj)
    
    asset_summary, account_table_items = get_asset_summary(db, username)
    result = {
        'asset_categories': list(set(asset_categories)),
        'asset_categories_sub': list(set(asset_categories_sub)),
        'trade_market': list(set(trade_market)),
        'trade_name': trade_name,
        # 'trade_code': list(set(trade_code)),
        'cashes': cashes,
        'exchange_name': list(set(exchange_name)),
        'exchange_code': list(set(exchange_code)),
        'currencies': list(set(currencies)),
        'asset_categories_obj': asset_categories_obj,
        'asset_summary': asset_summary,
        'account_table_items': account_table_items
    }
    # print('log_all:', log_all)
    # print('result:', result)
    
    # print('--------------------------------'*3)
    # pprint(asset_summary)
    # print('--------------------------------'*3)
    return result
    

@router.get("/trade_log", response_model=schemas.TradeLogPage)
def read_trades(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    code: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    asset_category: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # print('get_trade_logs_pagination:', current_user['username'], skip, limit, code, start_date, end_date, asset_category)
    print('asset_category:', asset_category)
    print('code:', code)
    result = crud.get_trade_logs_pagination(
        db=db,
        username=current_user['username'],
        skip=skip,
        limit=limit,
        code=code,
        start_date=start_date,
        end_date=end_date,
        asset_category=asset_category
    )
    # print('result:', len(result), result)
    return result


@router.get("/tax")
def calculate_tax(
    code: str,
    year: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    tax_data = trade_crud.get_trades_for_tax(
        db, 
        username=current_user['username'], 
        code=code, 
        year=year
    )
    return tax_data

@router.get("/get_fdr_price")
def read_fdr(
    codes: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    codes = codes.split(',')
    print('codes:', codes)
    
    fdr_data = get_fdr_price(codes)
    # for code in codes:
    #     fdr_data[code] = get_fdr_price_ten_days(code)
    #     print('fdr_data[code]:', fdr_data[code])
    #     price = fdr_data[code].iloc[-1]['Close']
    #       fdr_data[code] = price
    print('fdr_data:', fdr_data)
    # 가장 최근 날짜의 주가
    return fdr_data