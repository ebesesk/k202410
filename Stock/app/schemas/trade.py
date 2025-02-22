from pydantic import BaseModel, Field
from typing import Optional, Annotated, List
from datetime import date
from decimal import Decimal
from enum import Enum
# Trade 스키마
class TradeBase(BaseModel):
    date: date
    asset_category: Optional[str] = None
    market: Optional[str] = None
    code: str
    name: Optional[str] = None
    price: Decimal
    quantity: Decimal
    amount: Decimal
    action: str = 'in' or 'out'
    fee: Optional[Decimal] = Decimal('0.00')
    tax: Optional[Decimal] = Decimal('0.00')
    foreign_expense: Optional[Decimal] = Decimal('0.00')  # 국외 제비용 추가
    average_price: Optional[Decimal] = None
    username: str
    memo: Optional[str] = None

class TradeCreate(TradeBase):
    pass

class Trade(TradeBase):
    id: int

    class Config:
        orm_mode = True

# Dividend 스키마
class DividendBase(BaseModel):
    date: date
    amount: Decimal
    tax: Optional[Decimal] = Decimal('0.00')
    username: str
    memo: Optional[str] = None

class DividendCreate(DividendBase):
    trade_id: int

class Dividend(DividendBase):
    id: int
    trade_id: int

    class Config:
        orm_mode = True

# Transaction 스키마
class TransactionBase(BaseModel):
    date: date
    asset_category: Optional[str] = None
    currency: str
    amount: Decimal
    action: str
    interest: Optional[Decimal] = None
    fee: Optional[Decimal] = Decimal('0.00')
    tax: Optional[Decimal] = Decimal('0.00')
    username: str
    memo: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int

    class Config:
        orm_mode = True

# Exchange 스키마
class ExchangeBase(BaseModel):
    date: date
    asset_category: str
    currency_to_exchange: str
    currency_to_receive: str
    exchange_amount: Decimal
    exchange_rate: Decimal
    receive_amount: Decimal
    fee: Optional[Decimal] = Decimal('0.00')
    tax: Optional[Decimal] = Decimal('0.00')
    username: str
    memo: Optional[str] = None

class ExchangeCreate(ExchangeBase):
    pass

class Exchange(ExchangeBase):
    id: int

    class Config:
        orm_mode = True


class TaxTypeEnum(str, Enum):
    TRANSACTION = 'transaction'
    DIVIDEND = 'dividend'

class TaxBase(BaseModel):
    country: str
    asset_category: str
    tax_type: TaxTypeEnum  # 세금 유형
    tax_percentage: Decimal
    memo: Optional[str] = None

class TaxCreate(TaxBase):
    pass

class Tax(TaxBase):
    id: int

    class Config:
        orm_mode = True
        

class FeeBase(BaseModel):
    country: str
    asset_category: str
    fee_percentage: Decimal
    memo: Optional[str] = None

class FeeCreate(FeeBase):
    pass

class Fee(FeeBase):
    id: int

    class Config:
        orm_mode = True