# schemas/investment_schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List

class PaginationResponse(BaseModel):
    currentPage: int
    itemsPerPage: int
    totalItems: int
    totalPages: int

# Account Schema
class AccountBase(BaseModel):
    code: str
    name: str
    category: str
    type: str
    is_active: bool = True  # 계정 활성 여부
    username: Optional[str] = None
    account_metadata: Optional[Dict[str, Any]] = None  # 계정 추가 정보

class AccountCreate(AccountBase):
    pass
class AccountUpdate(AccountBase):
    id: int
    pass
class Account(AccountBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
# Response Models
class AccountResponse(Account):
    pass

# Asset Schema
class AssetBase(BaseModel):
    symbol: str   # 종목코드/티커
    name: str     # 종목명
    type: str     # 종목유형
    currency: str   # 통화
    exchange: Optional[str]  = None  # 거래소/마켓
    sector: Optional[str]  = None    # 섹터/카테고리
    is_active: bool = True  # 자산 활성 여부
    asset_metadata: Optional[Dict[str, Any]] = None  # 자산 추가 정보
    username: Optional[str] = None

class AssetCreate(AssetBase):
    pass

class Asset(AssetBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True



class AssetResponse(Asset):
    pass
# class FeeCreate(BaseModel):
#     type: str   # 수수료 유형
#     amount: float  # 수수료 금액
#     currency: str  # 수수료 통화
#     description: Optional[str] = None  # 수수료 설명

# class FeeResponse(FeeCreate):
#     id: int
#     transaction_id: int
#     created_at: datetime

#     class Config:
#         from_attributes = True

# class FeeListResponse(BaseModel):
#     items: List[FeeResponse]
#     pagination: PaginationResponse
    
# class FeeResponse(Fee):
#     id: int
#     created_at: datetime

#     class Config:
#         from_attributes = True

# Transaction Schema
class TransactionBase(BaseModel):
    date: datetime   # 거래일
    asset_id: Optional[int] = None
    type: str        # 거래유형 (EXCHANGE)
    quantity: Optional[float] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    exchange_rate: Optional[float] = None  # 환율
    amount: Optional[float] = None
    transaction_metadata: Optional[Dict[str, Any]] = None
    note: Optional[str] = None
    username: Optional[str] = None
    fees: Optional[Dict[str, Any]] = None  # 수수료 목록
    
    debit_account_id: int      # 차변 계정
    credit_account_id: int     # 대변 계정
    
    

class ExchangeTransactionCreate(TransactionBase):
    type: str = "EXCHANGE"  # 환전 거래 타입 고정
    from_currency: str      # 필수 필드로 변경
    to_currency: str        # 필수 필드로 변경
    from_amount: float      # 필수 필드로 변경
    to_amount: float        # 필수 필드로 변경
    exchange_rate: float    # 필수 필드로 변경
    
    
class TransactionCreate(TransactionBase):
    pass
class TransactionUpdate(TransactionBase):
    id: int
    pass

class Transaction(TransactionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True



# Position Schema
class PositionBase(BaseModel):
    asset_id: int
    quantity: float
    avg_price: float
    currency: str
    current_price: Optional[float] = None
    last_updated: Optional[datetime] = None
    position_metadata: Optional[Dict[str, Any]] = None

class PositionCreate(PositionBase):
    pass

class Position(PositionBase):
    id: int

    class Config:
        from_attributes = True

# ExchangeRate Schema
class ExchangeRateBase(BaseModel):
    from_currency: str
    to_currency: str
    rate: float
    date: datetime
    source: str

class ExchangeRateCreate(ExchangeRateBase):
    pass

class ExchangeRate(ExchangeRateBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True



# Portfolio Schema
class PortfolioBase(BaseModel):
    date: datetime
    total_value: float
    cash_value: float
    invested_value: float
    profit_loss: float
    portfolio_metadata: Optional[Dict[str, Any]] = None

class PortfolioCreate(PortfolioBase):
    pass

class Portfolio(PortfolioBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True




class ExchangeRateResponse(ExchangeRate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TransactionResponse(BaseModel):
    id: int
    date: datetime
    type: str
    quantity: Optional[float] = None
    price: Optional[float] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    exchange_rate: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


        





class TransactionListResponse(BaseModel):
    items: List[TransactionResponse]
    pagination: PaginationResponse

class AssetListResponse(BaseModel):
    items: List[AssetResponse]
    pagination: PaginationResponse

class AccountListResponse(BaseModel):
    items: List[AccountResponse]
    pagination: PaginationResponse

class PositionResponse(Position):
    asset: AssetResponse

class PortfolioResponse(Portfolio):
    pass


class ExchangeRateBase(BaseModel):
    from_currency: str
    to_currency: str
    rate: float
    date: datetime
    source: str
    transaction_id: Optional[int] = None  # transaction과의 관계를 위해 추가
    username: Optional[str] = None

class ExchangeRateCreate(ExchangeRateBase):
    pass

class ExchangeRate(ExchangeRateBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ExchangeRateResponse(ExchangeRate):
    transaction: Optional['TransactionResponse'] = None  # 순환 참조 방지를 위한 문자열 참조

    class Config:
        from_attributes = True

# class TransactionResponse(BaseModel):
#     id: int
#     date: datetime
#     type: str
#     quantity: Optional[float] = None
#     price: Optional[float] = None
#     amount: Optional[float] = None
#     currency: Optional[str] = None
#     exchange_rate: Optional[float] = None
#     exchange_rates: Optional[List[ExchangeRateResponse]] = None  # exchange_rates 관계 추가
#     created_at: datetime

#     class Config:
#         from_attributes = True