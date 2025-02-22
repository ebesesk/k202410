from pydantic import BaseModel, Field
from typing import Optional, Annotated, List
from datetime import date
from decimal import Decimal

class InterestStock(BaseModel):
    
    종목코드: Optional[Annotated[str, Field(min_length=6, max_length=6)]] = None  # 6자리로 제한
    한글기업명: Optional[str] = None
    시장구분: Optional[str] = None
    업종구분명: Optional[str] = None 
    tag: Optional[str] = None
    username: Optional[str] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True
        

class InterestStockCodes(BaseModel):
    codes: list[Annotated[str, Field(min_length=6, max_length=6)]]  # 리스트의 각 코드도 6자리로 제한

class InterestStockInput(BaseModel):
    key: Optional[str] = None
    code: Optional[str] = None

class InterestStockTag(BaseModel):
    종목코드: Optional[Annotated[str, Field(min_length=6, max_length=6)]] = None
    tag: Optional[str] = None
    username: Optional[str] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True


class AppKey(BaseModel):
    appkey: Optional[str] = None
    appsecretkey: Optional[str] = None
    cname: Optional[str] = None
    username: Optional[str] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True
        
class AppKeyRequest(BaseModel):
    cname: str
    username: str



# 주식 거래 로그
class Trade(BaseModel):
    date: date
    asset_category: str # stock, crypto, cash, exchange
    market: str     # KOSPI, KOSDAQ, NASDAQ, USD, KRW, 암호화폐 
    code: str       # 종목코드 042700 AAPL, BTC, USD, KRW
    name: str       # 종목명
    price: Decimal      # 주가
    quantity: Decimal   # 수량
    amount: Decimal     # 금액
    fee: Optional[Decimal] = 0
    tax: Optional[Decimal] = 0
    purchases_price: Optional[Decimal] = 0 # 매입 평균 단가
    dividend: Optional[Decimal] = 0 # 배당금
    action: str     # in, out   
    username: str = None
    memo: Optional[str] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True
        
class Dividend(BaseModel):
    date: date
    asset_category: str # stock, crypto, cash, exchange
    market: str     # KOSPI, KOSDAQ, NASDAQ, USD, KRW, 암호화폐 
    code: str       # 종목코드 042700 AAPL, BTC, USD, KRW
    name: str       # 종목명
    amount: Decimal # 배당금
    fee: Optional[Decimal] = 0
    tax: Optional[Decimal] = 0
    action: str     # in, out   
    username: str = None
    memo: Optional[str] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True
        
class Transaction(BaseModel):
    date: date 
    asset_category: str
    code: str
    name: str
    amount: Decimal
    action: str
    fee: Optional[Decimal] = 0
    tax: Optional[Decimal] = 0
    username: str = None
    memo: Optional[str] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True
    
class Exchange(BaseModel):
    date: date
    asset_category: str
    name: str  # 환전할 통화
    code: str  # 환전받을 통화
    quantity: Decimal  # 환전할 금액
    price: Decimal  # 환율
    amount: Decimal  # 환전받을 금액
    fee: Optional[Decimal] = 0
    tax: Optional[Decimal] = 0
    action: str
    username: str = None
    memo: Optional[str] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True

class TradeItem(BaseModel): 
    id: int
    date: date
    asset_category: str # stock, crypto, cash, exchange
    market: Optional[str] = None    # KOSPI, KOSDAQ, NASDAQ, USD, KRW, 암호화폐 
    code: str       # 종목코드 042700 AAPL, BTC, USD, KRW
    name: Optional[str] = None     # 종목명
    price: Optional[Decimal] = Field(default=None)
    quantity: Optional[Decimal] = Field(default=None)
    amount: Optional[Decimal] = Field(default=None)
    fee: Optional[Decimal] = Field(default=None)  # int -> Decimal 변환
    tax: Optional[Decimal] = Field(default=None)  # int -> Decimal 변환
    action: str
    memo: Optional[str] = None
    username: Optional[str] = None
    purchases_price: Optional[Decimal] = Field(default=None)
    holdings_quantity: Optional[Decimal] = Field(default=None)
    balance: Optional[Decimal] = Field(default=None)

    class Config:
        from_attributes = True
        populate_by_name = True

class TradeLogPage(BaseModel):
    total: int
    items: List[TradeItem]
    page: int
    pages: int
    has_next: bool
    has_prev: bool
    # trade_asset_category: Optional[List[str]] = None
    
    class Config:
        from_attributes = True
        
class DeleteTrade(BaseModel):
    id: int
    username: Optional[str] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True

class ExchangeLog(BaseModel):
    date: date
    asset_category: str
    code: str
    name: Optional[str] = None
    price: Decimal
    amount: Decimal
    action: bool
    fee: Optional[Decimal] = 0
    tax: Optional[Decimal] = 0
    balance: Optional[Decimal] = 0
    username: Optional[str] = None
    memo: Optional[str] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True