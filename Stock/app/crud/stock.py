from fastapi import Depends
from sqlalchemy.orm import Session
from app.utils.dependencies import get_db
from sqlalchemy import create_engine
from app.core.config import settings
from app.models.stock import Stocks, InterestStock, AppKey
from app.schemas import stock as schemas
import json
from sqlalchemy import or_





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
    print('stock:', stock)
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



# # 차트 데이터 조회
# def get_chart_data(db: Session, chart_data: schemas.ChartData):
#     return db.query(ChartData).filter(
#         ChartData.shcode == chart_data.shcode,
#         ChartData.username == chart_data.username,
#         ChartData.period == chart_data.period, 
#         ChartData.date == chart_data.date
#     ).first()
    
# # 차트 데이터 추가
# def insert_chart_data(db: Session, chart_data: schemas.ChartData):
#     db_chart_data = ChartData(
#         chart_data=chart_data.chart_data,
#         date=chart_data.date,
#         period=chart_data.period,
#         shcode=chart_data.shcode,
#         username=chart_data.username
#     )
#     db.add(db_chart_data)
#     db.commit()
#     db.refresh(db_chart_data)
#     return db_chart_data

# # 차트 데이터 삭제
# def delete_chart_data(db: Session, chart_data: schemas.ChartData):
#     db.query(ChartData).filter(
#         ChartData.shcode == chart_data.shcode,
#         ChartData.username == chart_data.username,
#         ChartData.period == chart_data.period, 
#         ChartData.date == chart_data.date
#     ).delete()
#     db.commit()
    
    