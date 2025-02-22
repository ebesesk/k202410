from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, not_
from typing import Optional
from datetime import datetime
from app.models.stock import TradeLog
from app.core.config import settings
from math import floor, trunc
import pprint
from decimal import Decimal
from app.schemas import stock as schemas
import copy
from app.crud import stock as crud
from app.crud import trade as crud_trade
from collections import defaultdict
import FinanceDataReader as fdr
from app.utils.fdr_util import get_fdr_price
from decimal import Decimal

def format_string(string):
    return string.lower().replace('.',',')


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
        if asset_category == 'stock':
            conditions.append(not_(TradeLog.asset_category.like('cash%')))
            conditions.append(not_(TradeLog.asset_category.like('exchange%')))
        else:
            print('asset_category:', asset_category)
            conditions.append(TradeLog.asset_category.like(asset_category + '%'))
    
    if conditions:
        query = query.filter(and_(*conditions))
    
    # 전체 아이템 수 계산
    total = query.count()
    
    # 정렬 및 페이지네이션 적용
    items = query.order_by(desc(TradeLog.date))\
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


def sign_trade_value(trade_log):
    
    if trade_log.fee:
        trade_log.fee = -abs(trade_log.fee)
    if trade_log.tax:
        trade_log.tax = -abs(trade_log.tax)
    
    if 'cash' not in trade_log.asset_category and 'exchange' not in trade_log.asset_category and 'dividend' not in trade_log.asset_category:
        if trade_log.action == 'in':
            trade_log.amount = -abs(trade_log.amount) # 매수 음수
            trade_log.quantity = abs(trade_log.quantity) # 매수 수량 양수
        elif trade_log.action == 'out':
            trade_log.amount = abs(trade_log.amount) # 매도 양수
            trade_log.quantity = -abs(trade_log.quantity) # 매도 수량 음수
    if 'cash' in trade_log.asset_category:
        if trade_log.action == 'in':
            trade_log.amount = abs(trade_log.amount) # 현금 입금 양수
        elif trade_log.action == 'out':
            trade_log.amount = -abs(trade_log.amount) # 현금 출금 음수

    if 'exchange' in trade_log.asset_category:
        if trade_log.action == 'in':
            trade_log.quantity = abs(trade_log.quantity) # 환전 (외화)매수 양수
            trade_log.amount = -abs(trade_log.amount) # 환전 (외화)매입 음수
        elif trade_log.action == 'out':
            trade_log.quantity = -abs(trade_log.quantity) # 환전 (외화)매도 음수
            trade_log.amount = abs(trade_log.amount) # 환전 (외화)매입 양수
    if 'dividend' in trade_log.asset_category:
        trade_log.amount = abs(trade_log.amount)
    # print('trade:', trade_log)
    return trade_log

def get_trade_log_fee_tax(trade_log):
    
    COMMISSION_RATE_STOCK_KR = Decimal(settings.COMMISSION_RATE_STOCK_KR)  # 증권 수수료
    TAX_RATE_STOCK_KR = Decimal(settings.TAX_RATE_STOCK_KR)  # 증권 세금
    COMMISSION_RATE_STOCK_US = Decimal(settings.COMMISSION_RATE_STOCK_US)  # 해외 수수료
    DIVIDEND_TAX_RATE_STOCK_KR = Decimal(settings.DIVIDEND_TAX_RATE_STOCK_KR)  # 배당 소득세
    DIVIDEND_TAX_RATE_STOCK_US = Decimal(settings.DIVIDEND_TAX_RATE_STOCK_US)  # 배당 소득세
    INTERNATIONAL_TRANSACTION_FEES = Decimal(settings.INTERNATIONAL_TRANSACTION_FEES)  # 해외 주식 수수료
    
    
    trade_log.asset_category = format_string(trade_log.asset_category)
    
    # 주식 거래 수수료 세금 계산
    if trade_log.asset_category.startswith('stock') and 'dividend' not in trade_log.asset_category:
        # 국내 주식 매수 매도 수수료 세금 계산
        if trade_log.action == 'in' and 'krw' in trade_log.asset_category: # 국내 주식 매수
            trade_log.fee = abs(trunc(trade_log.amount * COMMISSION_RATE_STOCK_KR)) * -1 # 소수점 버림 
            trade_log.tax = 0
        elif trade_log.action == 'out' and 'krw' in trade_log.asset_category: # 국내 주식 매도
            trade_log.fee = abs(trunc(trade_log.amount * COMMISSION_RATE_STOCK_KR)) * -1 # 소수점 버림 
            trade_log.tax = abs(trunc(trade_log.amount * TAX_RATE_STOCK_KR)) * -1 # 소수점 버림 
        
        # 해외 주식 매수 매도 수수료 세금 계산
        if trade_log.action == 'in' and 'usd' in trade_log.asset_category: # 해외 주식 매수
            trade_log.fee = abs(round(trade_log.amount * COMMISSION_RATE_STOCK_US, 2)) * -1
            trade_log.tax = 0
            print('trade_log.fee:', trade_log.fee)
            print('trade_log.tax:', trade_log.tax)
        elif trade_log.action == 'out' and 'usd' in trade_log.asset_category: # 해외 주식 매도
            trade_log.fee = abs(round(trade_log.amount * COMMISSION_RATE_STOCK_US, 2)) * -1
            trade_log.tax = abs(round(trade_log.amount * INTERNATIONAL_TRANSACTION_FEES, 2)) * -1
            print('trade_log.fee:', trade_log.fee)
            print('trade_log.tax:', trade_log.tax)
        
        # 배당 소득세 계산
        if trade_log.action == 'in' and 'dividend' in trade_log.asset_category and 'krw' in trade_log.asset_category: # 배당 수령
            trade_log.tax = abs(trunc(Decimal(trade_log.amount) * DIVIDEND_TAX_RATE_STOCK_KR)) * -1 # 소수점 버림
            trade_log.amount = abs(Decimal(trade_log.amount))
            print('trade_log.tax:', Decimal(trade_log.tax))
        elif trade_log.action == 'in' and 'dividend' in trade_log.asset_category and 'usd' in trade_log.asset_category: # 배당 수령
            trade_log.tax = abs(round(Decimal(trade_log.amount) * DIVIDEND_TAX_RATE_STOCK_US, 2)) * -1
            trade_log.amount = abs(Decimal(trade_log.amount))
            print('trade_log.tax:', Decimal(trade_log.tax))
    # if trade_log.asset_category.startswith('cash'):
    if trade_log.asset_category.startswith('exchange'):
        trade_log.fee = 0
        trade_log.tax = 0
    return trade_log


def get_asset_summary_old(db: Session, username: str):
    query = db.query(TradeLog).filter(TradeLog.username == username).all()
    
    
    
    trade_summary = {}
    transaction_summary = {}
    exchange_summary = {}    
    summary = {}
    
    #
    
    total_amount = {}
    cash_amount = {}
    exchange_amount = {}
    stock_amount = {}
    # crypto_amount = {}
    
    # 키 생성 함수
    def make_keys(total, sub, currency, trade):
        # 수수료, 세금 초기화
        if trade.fee == None:
            trade.fee = Decimal(0)
        if trade.tax == None:
            trade.tax = Decimal(0)
        # 키 생성
        if currency not in sub:
            sub[currency] = {}
            sub[currency]['amount'] = Decimal(0)
            sub[currency]['fee'] = Decimal(0)
            sub[currency]['tax'] = Decimal(0)
            sub[currency]['balance'] = Decimal(0)
        # 총합 키 생성
        if currency not in total:
            total[currency] = {}
            total[currency]['amount'] = Decimal(0)
            total[currency]['fee'] = Decimal(0)
            total[currency]['tax'] = Decimal(0)
            total[currency]['balance'] = Decimal(0) 
        # # 서브 키 값 계산
        # sub[currency]['amount'] += trade.amount
        # sub[currency]['fee'] += trade.fee
        # sub[currency]['tax'] += trade.tax
        # sub[currency]['balance'] += (trade.amount + trade.fee + trade.tax)
        
        # # 총합 키 값 계산
        # total[currency]['amount'] += trade.amount
        # total[currency]['fee'] += trade.fee
        # total[currency]['tax'] += trade.tax
        # total[currency]['balance'] += (trade.amount + trade.fee + trade.tax)
                
                
          
    for trade in query:
        category = format_string(trade.asset_category)  # cash.krw, cash.usd, stock.krw, stock.usd, exchange.krw, exchange.usd
        # print('category:', category)
        # 현금 예수금 계산
        if category.startswith('cash'):
            make_keys(total_amount, cash_amount, trade.code, trade)
            # 서브 키 값 계산
            cash_amount[trade.code]['amount'] += trade.amount
            cash_amount[trade.code]['fee'] += trade.fee
            cash_amount[trade.code]['tax'] += trade.tax
            cash_amount[trade.code]['balance'] += (trade.amount + trade.fee + trade.tax)
            
            # 총합 키 값 계산
            total_amount[trade.code]['amount'] += trade.amount
            total_amount[trade.code]['fee'] += trade.fee
            total_amount[trade.code]['tax'] += trade.tax
            total_amount[trade.code]['balance'] += (trade.amount + trade.fee + trade.tax)

        # 환전 예수금 계산
        if category.startswith('exchange'):
            # 환전 받는 예수금 계산
            make_keys(total_amount, exchange_amount, trade.code, trade)
            # 서브 키 값 계산
            exchange_amount[trade.code]['amount'] += trade.amount
            exchange_amount[trade.code]['fee'] += trade.fee
            exchange_amount[trade.code]['tax'] += trade.tax
            exchange_amount[trade.code]['balance'] += (trade.amount + trade.fee + trade.tax)
            
            # 총합 키 값 계산
            total_amount[trade.code]['amount'] += trade.amount
            total_amount[trade.code]['fee'] += trade.fee
            total_amount[trade.code]['tax'] += trade.tax
            total_amount[trade.code]['balance'] += (trade.amount + trade.fee + trade.tax)

            # 환전 주는 예수금 계산
            make_keys(total_amount, exchange_amount, trade.name, trade)
            # 서브 키 값 계산
            exchange_amount[trade.name]['amount'] += trade.quantity
            exchange_amount[trade.name]['fee'] += trade.fee
            exchange_amount[trade.name]['tax'] += trade.tax
            exchange_amount[trade.name]['balance'] += (trade.quantity + trade.fee + trade.tax)
            
            # 총합 키 값 계산
            total_amount[trade.name]['amount'] += trade.quantity
            total_amount[trade.name]['fee'] += trade.fee
            total_amount[trade.name]['tax'] += trade.tax
            total_amount[trade.name]['balance'] += (trade.quantity + trade.fee + trade.tax)

        # 주식 예수금 계산
        # if 'cash' not in category and 'exchange' not in category:
        if not category.startswith('exchange') and not category.startswith('cash'):
            currency = category.split(',')[-1].upper()

            make_keys(total_amount, stock_amount, currency, trade)
    
            # 서브 키 값 계산
            stock_amount[currency]['amount'] += trade.amount
            stock_amount[currency]['fee'] += trade.fee
            stock_amount[currency]['tax'] += trade.tax
            stock_amount[currency]['balance'] += (trade.amount + trade.fee + trade.tax)
            
            # 총합 키 값 계산
            total_amount[currency]['amount'] += trade.amount
            total_amount[currency]['fee'] += trade.fee
            total_amount[currency]['tax'] += trade.tax
            total_amount[currency]['balance'] += (trade.amount + trade.fee + trade.tax)

    
    
    total_amount['cash'] = cash_amount
    total_amount['exchange'] = exchange_amount
    total_amount['stock'] = stock_amount
    
    
    # pprint.pprint(total_amount)       
    return {
        'total_amount': total_amount
    }
    
from collections import defaultdict
from decimal import Decimal

def nested_dict():
    return defaultdict(nested_dict)

def get_asset_summary_old2(db: Session, username: str):
    # 중첩된 defaultdict 생성
    asset_summary = defaultdict(lambda: {
        'total': Decimal(0),
        'sub': [],
        'currency': defaultdict(lambda: {'balance': Decimal(0)}),
    })

    # # cash와 exchange를 위한 특별한 구조
    # asset_summary['CASH'] = defaultdict(lambda: {'balance': Decimal(0), 'name': ''})
    # asset_summary['EXCHANGE'] = {
    #     'currency': defaultdict(lambda: {'balance': Decimal(0)})
    # }

    asset_summary = {
        'foreign': {
            'total': {
                'name': 'foreign',
                'balance': {},
            },
        
            'account': {
                'name': '',
                'asset_category': 'cash',
                'balance': {},
            },

            'exchange': {
                'asset_category': 'exchange',
                'balance': {},
            },
            
            'asset(stock)': {
                'asset_category': 'stock.usd',
                'balance': {},
            },
        },
        'local': {
            'total': {
                'name': 'local',
                'balance': {},
            },
            'account': {
                'name': '',
                'asset_category': 'cash',
                'balance': {},
            },
            'asset(stock)': {
                'asset_category': 'stock.krw',
                'balance': {},
            },
        }
    }
    pprint.pprint(asset_summary)    
    
    trades = db.query(TradeLog).filter(
        TradeLog.username == username
    ).order_by(TradeLog.date.desc(), TradeLog.id.desc()).all()

    for trade in trades:
        categories = trade.asset_category.upper().split(',')
        asset = categories[0].strip()
        sub = categories[1].strip() if len(categories) > 2 else ''
        currency = categories[-1].strip()


        # 현금 계좌 
        if asset == 'CASH':

            # 외화 현금 계좌
            if trade.code == 'foreign':
                '''trade.code foreign or local'''
                # 계좌 이름
                asset_summary['foreign']['account']['name'] = trade.name
                # 계좌 잔액
                try:
                    asset_summary['foreign']['account']['balance'][currency] += trade.amount  # 계좌
                except KeyError:
                    asset_summary['foreign']['account']['balance'] = {currency: Decimal(0)}
                    asset_summary['foreign']['account']['balance'][currency] += trade.amount
                try:    
                    asset_summary['foreign']['total']['balance'][currency] += trade.amount  # 총합
                except KeyError:
                    asset_summary['foreign']['total']['balance'] = {currency: Decimal(0)}
                    asset_summary['foreign']['total']['balance'][currency] += trade.amount

            # 국내 현금 계좌
            elif trade.code == 'local':
                # 계좌 이름
                asset_summary['local']['account']['name'] = trade.name
                # 계좌 잔액
                try:    
                    asset_summary['local']['account']['balance'][currency] += trade.amount  # account(cash)
                except KeyError:
                    asset_summary['local']['account']['balance'] = {currency: Decimal(0)}
                    asset_summary['local']['account']['balance'][currency] += trade.amount
                try:
                    asset_summary['local']['total']['balance'][currency] += trade.amount  # total
                except KeyError:
                    asset_summary['local']['total']['balance'] = {currency: Decimal(0)}
                    asset_summary['local']['total']['balance'][currency] += trade.amount
        
        # 환전 
        elif asset == 'EXCHANGE':
            '''
            외환 계좌에만 적용
            '''
            # 원화 외화 입출금
            try:
                asset_summary['foreign']['exchange']['balance'][trade.code.upper()] += trade.amount
            except KeyError:
                asset_summary['foreign']['exchange']['balance'][trade.code.upper()] = {'balance': Decimal(0)}
                asset_summary['foreign']['exchange']['balance'][trade.code.upper()]['balance'] += trade.amount
            try:
                asset_summary['foreign']['exchange']['balance'][trade.name.upper()] += trade.quantity
            except KeyError:
                asset_summary['foreign']['exchange']['balance'][trade.name.upper()] = {'balance': Decimal(0)}
                asset_summary['foreign']['exchange']['balance'][trade.name.upper()]['balance'] += trade.quantity
            
            
            
        # else:
        #     asset_summary[asset]['currency'][currency]['balance'] += trade.amount
            
        #     if sub and sub not in asset_summary[asset]['sub']:
        #         asset_summary[asset]['sub'].append(sub)

    print('--------------------------------'*3)
    pprint.pprint(dict(asset_summary))
    print('--------------------------------'*3)

    # defaultdict를 일반 dict로 변환
    # return {
    #     k: (
    #         dict(v) if k == 'CASH' else
    #         {
    #             'currency': dict(v['currency']) if isinstance(v.get('currency'), defaultdict) else v['currency'],
    #             'sub': v.get('sub', []),
    #             'total': v.get('total', Decimal(0))
    #         }
    #     )
    #     for k, v in asset_summary.items()
    # }

def get_asset_summary(db: Session, username: str):

    trades = db.query(TradeLog).filter(
        TradeLog.username == username
    ).order_by(TradeLog.date.desc(), TradeLog.id.desc()).all()

    
    currency_list = crud_trade.get_currency_list(db, username)
    # print('currency_list:', currency_list)
    asset_list = crud_trade.get_asset_list(db, username)
    # sub_list = crud.get_asset_sub_list(db, username, asset_list[0])
    
    # 가장 최근 거래 
    stock_dict = {}
    for trade in trades:
        if trade.code not in stock_dict:
            stock_dict[trade.code] = {
                'purchases_price': trade.purchases_price,
                'id': trade.id,
                'date': trade.date,
            }
        else:
            if stock_dict[trade.code]['date'] < trade.date:
                stock_dict[trade.code] = {
                    'purchases_price': trade.purchases_price,
                    'id': trade.id,
                    'date': trade.date,
                }
            elif stock_dict[trade.code]['date'] == trade.date:
                if stock_dict[trade.code]['id'] < trade.id:
                    stock_dict[trade.code] = {
                        'purchases_price': trade.purchases_price,
                        'id': trade.id,
                        'date': trade.date,
                    }
    
    
    
    asset_summary = {}
    asset_summary['foreign'] = {}
    asset_summary['foreign']['account'] = {}
    asset_summary['foreign']['account']['name'] = ''
    asset_summary['local'] = {}
    asset_summary['local']['account'] = {}
    asset_summary['local']['krw'] = {}
    asset_summary['local']['krw']['balance'] = Decimal(0)
    asset_summary['local']['krw']['fee'] = Decimal(0)
    asset_summary['local']['krw']['tax'] = Decimal(0)

    for currency in currency_list:
        asset_summary['foreign'][currency] = {}
        asset_summary['foreign'][currency]['balance'] = Decimal(0)
        asset_summary['foreign'][currency]['fee'] = Decimal(0)
        asset_summary['foreign'][currency]['tax'] = Decimal(0)

    for i, trade in enumerate(trades):
        
        asset = (trade.asset_category + ',').split(',')[0]
        
        # sub = (trade.asset_category + ',').split(',')[1]
        
        currency = trade.asset_category.split(',')[-1]
        if currency not in currency_list:
            currency = ''
        
        sub = ''
        for curr in currency_list:
            sub = trade.asset_category.replace(currency, '').replace(asset, '').replace(',', '')
            

        
        # print('currency:', currency)
        
        if not trade.fee:
            trade.fee = Decimal(0)
        if not trade.tax:
            trade.tax = Decimal(0)


        if asset == 'exchange':
            try:
                asset_summary['foreign']['exchange'][trade.code.lower()] += trade.amount
                asset_summary['foreign']['exchange'][trade.name.lower()] += trade.quantity  
            except KeyError:
                asset_summary['foreign']['exchange'] = {}
                asset_summary['foreign']['exchange'][trade.code.lower()] = Decimal(0)
                asset_summary['foreign']['exchange'][trade.name.lower()] = Decimal(0)
                asset_summary['foreign']['exchange'][trade.code.lower()] += trade.amount
                asset_summary['foreign']['exchange'][trade.name.lower()] += trade.quantity 
                
            asset_summary['foreign'][trade.code.lower()]['balance'] += trade.amount
            asset_summary['foreign'][trade.name.lower()]['balance'] += trade.quantity
            # asset_summary['foreign'][trade.name.lower()]['exchange'] 
            
            
            
        elif asset == 'cash':
            if trade.code == 'local':
                asset_summary['local'][currency]['balance'] += trade.amount + trade.fee + trade.tax
                asset_summary['local'][currency]['fee'] += trade.fee
                asset_summary['local'][currency]['tax'] += trade.tax
                asset_summary['local']['account']['name'] = trade.name
            elif trade.code == 'foreign':
                asset_summary['foreign'][currency]['balance'] += trade.amount + trade.fee + trade.tax
                asset_summary['foreign'][currency]['fee'] += trade.fee
                asset_summary['foreign'][currency]['tax'] += trade.tax
                asset_summary['foreign']['account']['name'] = trade.name
                
            if sub and trade.code == 'foreign':
                # print('sub:', sub)
                try:
                    asset_summary['foreign']['account']
                except KeyError:
                    asset_summary['foreign']['account'] = {}
                try:    
                    asset_summary['foreign']['account']['total']
                except KeyError:
                    asset_summary['foreign']['account']['total'] = {}
                try:
                    asset_summary['foreign']['account']['total'][currency] 
                except KeyError:
                    asset_summary['foreign']['account']['total'][currency] = {}
                try: 
                    asset_summary['foreign']['account'][sub]
                except KeyError:
                    asset_summary['foreign']['account'][sub] = {}
                try:
                    asset_summary['foreign']['account'][sub][currency]
                except KeyError:
                    asset_summary['foreign']['account'][sub][currency] = {}
                
                    
                    asset_summary['foreign']['account']['total'][currency] = {}
                    asset_summary['foreign']['account']['total'][currency]['balance'] = Decimal(0)
                    asset_summary['foreign']['account']['total'][currency]['fee'] = Decimal(0)
                    asset_summary['foreign']['account']['total'][currency]['tax'] = Decimal(0)
                    asset_summary['foreign']['account'][sub][currency] = {}
                    asset_summary['foreign']['account'][sub][currency]['balance'] = Decimal(0)
                    asset_summary['foreign']['account'][sub][currency]['fee'] = Decimal(0)
                    asset_summary['foreign']['account'][sub][currency]['tax'] = Decimal(0)
               
                asset_summary['foreign']['account']['total'][currency]['balance'] += trade.amount + trade.fee + trade.tax
                asset_summary['foreign']['account']['total'][currency]['fee'] += trade.fee
                asset_summary['foreign']['account']['total'][currency]['tax'] += trade.tax
                asset_summary['foreign']['account'][sub][currency]['balance'] += trade.amount + trade.fee + trade.tax
                asset_summary['foreign']['account'][sub][currency]['fee'] += trade.fee
                asset_summary['foreign']['account'][sub][currency]['tax'] += trade.tax
                
            if sub and trade.code == 'local':
                try:
                    asset_summary['local']['account'][sub]['balance'] += trade.amount + trade.fee + trade.tax
                    asset_summary['local']['account'][sub]['fee'] += trade.fee
                    asset_summary['local']['account'][sub]['tax'] += trade.tax
                    asset_summary['local']['account'][sub]['total']['balance'] += trade.amount + trade.fee + trade.tax
                    asset_summary['local']['account'][sub]['total']['fee'] += trade.fee
                    asset_summary['local']['account'][sub]['total']['tax'] += trade.tax
                    # asset_summary['local']['account']['balance'] += trade.amount
                    # asset_summary['local']['account']['fee'] += trade.fee
                    # asset_summary['local']['account']['tax'] += trade.tax
                except KeyError:
                    asset_summary['local']['account'][sub] = {}
                    asset_summary['local']['account'][sub]['balance'] = Decimal(0)
                    asset_summary['local']['account'][sub]['fee'] = Decimal(0)
                    asset_summary['local']['account'][sub]['tax'] = Decimal(0)
                    asset_summary['local']['account'][sub]['balance'] += trade.amount + trade.fee + trade.tax
                    asset_summary['local']['account'][sub]['fee'] += trade.fee
                    asset_summary['local']['account'][sub]['tax'] += trade.tax
                    
                    asset_summary['local']['account']['total'] = {}
                    asset_summary['local']['account']['total']['balance'] = Decimal(0)
                    asset_summary['local']['account']['total']['fee'] = Decimal(0)
                    asset_summary['local']['account']['total']['tax'] = Decimal(0)
                    asset_summary['local']['account']['total']['balance'] += trade.amount + trade.fee + trade.tax
                    asset_summary['local']['account']['total']['fee'] += trade.fee
                    asset_summary['local']['account']['total']['tax'] += trade.tax

        
        
        
        
        
        else:
            # 계좌 잔액 계산
            if currency == 'krw':
                asset_summary['local'][currency]['balance'] += trade.amount + trade.fee + trade.tax
                asset_summary['local'][currency]['fee'] += trade.fee
                asset_summary['local'][currency]['tax'] += trade.tax
            else:
                asset_summary['foreign'][currency]['balance'] += trade.amount + trade.fee + trade.tax
                asset_summary['foreign'][currency]['fee'] += trade.fee
                asset_summary['foreign'][currency]['tax'] += trade.tax
            if sub and not trade.price and not trade.quantity and trade.amount > 0:
                if currency != 'krw':
                    _key = 'foreign'
                else:
                    _key = 'local'
                
                try:
                    asset_summary[_key][asset]
                except KeyError:
                    asset_summary[_key][asset] = {}
                try:
                    asset_summary[_key][asset][sub]
                except KeyError:
                    asset_summary[_key][asset][sub] = {}
                
                try:
                    asset_summary[_key][asset][sub][currency]
                except KeyError:
                    asset_summary[_key][asset][sub][currency] = {}
                
                # try:
                #     asset_summary[_key][asset][sub]['total']
                # except KeyError:
                #     asset_summary[_key][asset][sub]['total'] = {}
                
                try:
                    asset_summary[_key][asset][sub][currency]['balance'] += trade.amount + trade.fee + trade.tax
                    asset_summary[_key][asset][sub][currency]['fee'] += trade.fee
                    asset_summary[_key][asset][sub][currency]['tax'] += trade.tax
                    # asset_summary[_key][asset][sub][currency]['balance'] += trade.amount
                    # asset_summary[_key][asset][sub][currency]['fee'] += trade.fee
                    # asset_summary[_key][asset][sub][currency]['tax'] += trade.tax
                except KeyError:

                    asset_summary[_key][asset][sub][currency]['balance'] = Decimal(0)
                    asset_summary[_key][asset][sub][currency]['fee'] = Decimal(0)
                    asset_summary[_key][asset][sub][currency]['tax'] = Decimal(0)
                    asset_summary[_key][asset][sub][currency]['balance'] += trade.amount + trade.fee + trade.tax
                    asset_summary[_key][asset][sub][currency]['fee'] += trade.fee
                    asset_summary[_key][asset][sub][currency]['tax'] += trade.tax
                    
                    # # asset_summary[_key][asset][currency][sub] = {}
                    # asset_summary[_key][asset][sub][currency]['balance'] = Decimal(0)
                    # asset_summary[_key][asset][sub][currency]['fee'] = Decimal(0)
                    # asset_summary[_key][asset][sub][currency]['tax'] = Decimal(0)
                    # asset_summary[_key][asset][sub][currency]['balance'] += trade.amount
                    # asset_summary[_key][asset][sub][currency]['fee'] += trade.fee
                    # asset_summary[_key][asset][sub][currency]['tax'] += trade.tax
            else:
                if currency != 'krw':
                    _key = 'foreign'
                else:
                    _key = 'local'
                
                # 주식 보유수량 0인 마지막 거래 찾기
                _stock_date = crud_trade.get_latest_trade_by_code_zero_holdings(db, username, trade.code)
                
                # 주식 최초 거래 이후 거래인 경우 건너뜀
                if _stock_date and trade.id <= _stock_date.id:
                    # print('skip:', trade.code, trade.id, trade.date, _stock_id, _stock_date.date, _stock_date.id)
                    continue
                
                
                
                try:
                    asset_summary[_key][asset]
                except KeyError:
                    asset_summary[_key][asset] = {}
                    
                try:
                    asset_summary[_key][asset]['item']
                except KeyError:
                    asset_summary[_key][asset]['item'] = {}

                try:
                    asset_summary[_key][asset]['item'][trade.name]
                except KeyError:
                    asset_summary[_key][asset]['item'][trade.name] = {}
                
                try:
                    asset_summary[_key][asset]['item'][trade.name][currency]
                except KeyError:
                    asset_summary[_key][asset]['item'][trade.name][currency] = {}
                    asset_summary[_key][asset]['item'][trade.name][currency]['code'] = ''
                    asset_summary[_key][asset]['item'][trade.name][currency]['quantity'] = Decimal(0)
                    asset_summary[_key][asset]['item'][trade.name][currency]['balance'] = Decimal(0)
                    asset_summary[_key][asset]['item'][trade.name][currency]['fee'] = Decimal(0)
                    asset_summary[_key][asset]['item'][trade.name][currency]['tax'] = Decimal(0)
                    asset_summary[_key][asset]['item'][trade.name][currency]['purchases_price'] = Decimal(0)
                    # asset_summary[_key][asset]['item'][trade.name][currency]['price'] = Decimal(0)

                try:
                    if trade.code in stock_dict.keys():  # 주식 가장 최근 거래
                        asset_summary[_key][asset]['item'][trade.name][currency]['purchases_price'] = stock_dict[trade.code]['purchases_price']
                        # asset_summary[_key][asset]['item'][trade.name][currency]['price'] = get_fdr_price(trade.code)[trade.code]
                    else:
                        asset_summary[_key][asset]['item'][trade.name][currency]['purchases_price'] = Decimal(0)
                    asset_summary[_key][asset]['item'][trade.name][currency]['code'] = trade.code
                    asset_summary[_key][asset]['item'][trade.name][currency]['quantity'] += trade.quantity
                    asset_summary[_key][asset]['item'][trade.name][currency]['balance'] += trade.amount + trade.fee + trade.tax
                    asset_summary[_key][asset]['item'][trade.name][currency]['fee'] += trade.fee
                    asset_summary[_key][asset]['item'][trade.name][currency]['tax'] += trade.tax

                except KeyError:
                    asset_summary[_key][asset]['item'][trade.name][currency]['quantity'] = Decimal(0)
                    asset_summary[_key][asset]['item'][trade.name][currency]['balance'] = Decimal(0)
                    asset_summary[_key][asset]['item'][trade.name][currency]['fee'] = Decimal(0)
                    asset_summary[_key][asset]['item'][trade.name][currency]['tax'] = Decimal(0)
                    asset_summary[_key][asset]['item'][trade.name][currency]['quantity'] += trade.quantity
                    asset_summary[_key][asset]['item'][trade.name][currency]['balance'] += trade.amount + trade.fee + trade.tax
                    asset_summary[_key][asset]['item'][trade.name][currency]['fee'] += trade.fee
                    asset_summary[_key][asset]['item'][trade.name][currency]['tax'] += trade.tax
                
    print('--------------------------------'*3)
    # pprint.pprint(asset_summary)
    print('--------------------------------'*3)
    
    account_table_items = {}
    for _key, _value in asset_summary.items():
        for _key, _value in _value.items():
            if _key not in currency_list and _key != 'account' and _key != 'exchange':
                for _key, _value in _value['item'].items():
                    # print('_key:', _key)
                    for _key, _value in _value.items():
                        # print('_key:', _key)
                        # print('_value:', _value)
                        try:
                            account_table_items[_key]
                        except KeyError:
                            account_table_items[_key] = []
                        # print(_key, _value)
                        try:
                            price = get_fdr_price(db, _value['code'])[_value['code']]
                            # print('price:', price, type(price))
                            price = Decimal(str(price))
                        except KeyError:
                            price = Decimal(0)
                        
                        account_table_items[_key].append(
                            {
                                'code': _value['code'],
                                'quantity': _value['quantity'],
                                'purchases_price': _value['purchases_price'],
                                'purchases_amount': _value['purchases_price'] * _value['quantity'],
                                'price': price,
                                'amount': price * _value['quantity'],
                                'valuation_gain': (price * _value['quantity']) - (_value['purchases_price'] * _value['quantity']),
                                # 수익률 계산 시 0으로 나누기 방지
                                'return_rate': (((price * _value['quantity']) - (_value['purchases_price'] * _value['quantity'])) / (_value['purchases_price'] * _value['quantity']) * 100) if (_value['purchases_price'] and _value['quantity'] and _value['purchases_price'] * _value['quantity'] != 0) else 0,
                                'fee': _value['fee'],
                                'tax': _value['tax']
                            }
                        )
    # pprint.pprint(account_table_items)
    return asset_summary, account_table_items
    '''
    {'foreign': {'account': {'deposit': {'balance': Decimal('14500000.0000000000'),
                                           'fee': Decimal('0'),
                                           'tax': Decimal('0')},
                               'name': 'LS외화증권',
                               'total': {'balance': Decimal('14500000.0000000000'),
                                         'fee': Decimal('0'),
                                         'tax': Decimal('0')}},
             'exchange': {'krw': Decimal('-14499988.0000000000'),
                          'usd': Decimal('10188.3000000000')},
             'krw': {'balance': Decimal('12.0000000000'),
                     'fee': Decimal('0'),
                     'tax': Decimal('0')},
             'stock': {'dividend': {'balance': Decimal('6.0000000000'),
                                    'fee': Decimal('0'),
                                    'tax': Decimal('-0.9000000000')},
                       'item': {'구글': {'balance': Decimal('-2841.0900000000'),
                                       'fee': Decimal('-18.4600000000'),
                                       'quantity': Decimal('16.0000000000'),
                                       'tax': Decimal('-0.0700000000')},
                                '마소': {'balance': Decimal('-3527.6400000000'),
                                       'fee': Decimal('-24.2100000000'),
                                       'quantity': Decimal('8.0000000000'),
                                       'tax': Decimal('-0.0900000000')},
                                '메타': {'balance': Decimal('-3756.2600000000'),
                                       'fee': Decimal('-21.3800000000'),
                                       'quantity': Decimal('6.0000000000'),
                                       'tax': Decimal('-0.0700000000')}},
                       'total': {'balance': Decimal('6.0000000000'),
                                 'fee': Decimal('0'),
                                 'tax': Decimal('-0.9000000000')}},
             'usd': {'balance': Decimal('4.1300000000'),
                     'fee': Decimal('-64.0500000000'),
                     'tax': Decimal('-1.1300000000')}},
 'local': {'account': {'deposit': {'balance': Decimal('28057616.0000000000'),
                                         'fee': Decimal('0'),
                                         'tax': Decimal('0')},
                             'name': 'LS증권',
                             'total': {'balance': Decimal('28057616.0000000000'),
                                       'fee': Decimal('0'),
                                       'tax': Decimal('0')}},
           'krw': {'balance': Decimal('6178.0000000000'),
                   'fee': Decimal('-5484.0000000000'),
                   'tax': Decimal('-6404.0000000000')},
           'stock': {'item': {'제룡전기': {'balance': Decimal('-26848150.0000000000'),
                                       'fee': Decimal('-4540.0000000000'),
                                       'quantity': Decimal('652.0000000000'),
                                       'tax': Decimal('-2571.0000000000')},
                              '한미반도체': {'balance': Decimal('-1191400.0000000000'),
                                        'fee': Decimal('-944.0000000000'),
                                        'quantity': Decimal('23.0000000000'),
                                        'tax': Decimal('-3833.0000000000')}}}}}
    '''

  
def insert_trade_log(db: Session, exchange_log: schemas.Exchange):
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
    
    code_exchange_log = copy.deepcopy(exchange_log)
    code_exchange_log.asset_category = exchange_log.asset_category + ',' + exchange_log.code.lower()
    code_exchange_log.name = None
    code_exchange_log.quantity = None
    crud.insert_exchange(db, code_exchange_log)
    
    name_exchange_log = copy.deepcopy(exchange_log)
    name_exchange_log.asset_category = exchange_log.asset_category + ',' + exchange_log.name.lower()
    name_exchange_log.code = exchange_log.name
    name_exchange_log.amount = exchange_log.quantity
    name_exchange_log.name = None
    name_exchange_log.quantity = None
    crud.insert_exchange(db, name_exchange_log)
    
    return exchange_log

# 양도소득 계산
def calculate_capital_gains(trades):
    # FIFO (First In First Out) 방식으로 매수-매도 매칭
    buy_queue = []  # (수량, 매수가, 매수일) 저장
    capital_gains = []  # (매도수량, 매수가, 매도가, 보유기간) 저장
    
    for trade in trades:
        if trade.action == 'in':
            # 매수 시: 큐에 추가
            buy_queue.append({
                'quantity': trade.quantity,
                'price': trade.price,
                'date': trade.date,
                'fee': trade.fee
            })
            print('buy_queue:', buy_queue)
        else:
            print('buy_queue:', buy_queue)
            # 매도 시: FIFO로 매수 내역과 매칭
            remaining_quantity = trade.quantity
            while remaining_quantity > 0:
                oldest_buy = buy_queue[0]
                matched_quantity = min(remaining_quantity, oldest_buy['quantity'])
                print('matched_quantity:', matched_quantity)
                # 양도소득 계산
                gain = {
                    'quantity': matched_quantity,
                    'buy_price': oldest_buy['price'],
                    'sell_price': trade.price,
                    'buy_date': oldest_buy['date'],
                    'sell_date': trade.date,
                    'buy_fee': oldest_buy['fee'],
                    'sell_fee': trade.fee,
                    'sell_tax': trade.tax
                }
                capital_gains.append(gain)

                remaining_quantity -= matched_quantity
                oldest_buy['quantity'] -= matched_quantity
                
                if oldest_buy['quantity'] == 0:
                    buy_queue.pop(0)
    
    return capital_gains