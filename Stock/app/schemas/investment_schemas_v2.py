from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

# dictionary
class TransactionDict(BaseModel):
    id: int
    date: datetime
    asset_id: Optional[int] = None
    type: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    exchange_rate: Optional[float] = None
    amount: float
    transaction_metadata: Optional[Dict[str, Any]] = None
    note: Optional[str] = None
    fees: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    debit_account_id: int
    credit_account_id: int
    
    class Config:
        from_attributes = True

# pagination
class Pagination(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int

class AssetBase(BaseModel):
    id: int
    symbol: str
    name: str
    type: str
    currency: str
    exchange: str
    sector: str
    asset_metadata: Dict[str, Any]
    is_active: bool
    created_at: datetime
    username: str
    
    class Config:
        from_attributes = True

# 기본 거래 스키마
class TransactionBase(BaseModel):
    date: datetime
    type: str
    currency: str
    amount: float
    note: Optional[str] = None
    username: Optional[str] = None
    debit_account_id: int
    credit_account_id: int
    fees: Optional[Dict[str, Any]] = None

# 1. 현금 거래 (입출금, 수익, 비용)
class CashTransactionCreate(TransactionBase):
    # type: str = Field(..., description="DEPOSIT, WITHDRAW, INCOME, EXPENSE")
    transaction_metadata: Optional[Dict[str, Any]] = None

class CashTransactionResponse(CashTransactionCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True



class ExchangeRateTransactionBase(BaseModel):
    date: datetime
    type: str
    currency: str
    amount: float
    quantity: float
    exchange_rate: float
    note: Optional[str] = None
    debit_account_id: int
    credit_account_id: int
    fees: Optional[Dict[str, Any]] = None
    transaction_metadata: Optional[Dict[str, Any]] = None
    username: Optional[str] = None
    
class ExchangeRateTransactionCreate(ExchangeRateTransactionBase):
    pass

class ExchangeRateTransactionResponse(ExchangeRateTransactionCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ExchangeRateTransactionUpdate(ExchangeRateTransactionBase):
    id: int
    pass






# 2. 환전 거래
class ExchangeRateBase(BaseModel):
    from_currency: str
    to_currency: str
    rate: float
    date: datetime
    source: Optional[str] = None

class ExchangeRateCreate(ExchangeRateBase):
    username: Optional[str] = None

class ExchangeRateUpdate(BaseModel):
    from_currency: Optional[str] = None
    to_currency: Optional[str] = None
    rate: Optional[float] = None
    date: Optional[datetime] = None
    source: Optional[str] = None

class ExchangeRateInDB(ExchangeRateBase):
    id: int
    created_at: datetime
    username: str
    transaction_id: Optional[int] = None

    class Config:
        from_attributes = True





# 3. 증권 거래 (주식, ETF, 암호화폐)
class SecurityTransactionCreate(TransactionBase):
    id: Optional[int] = None
    type: str = Field(..., description="STOCK_BUY, STOCK_SELL, CRYPTO_BUY, CRYPTO_SELL")
    asset_id: int
    quantity: float
    price: float
    exchange_rate: Optional[float] = None
    transaction_metadata: Optional[Dict[str, Any]] = None
    get_info: bool = False

class SecurityTransactionResponse(SecurityTransactionCreate):
    id: int
    created_at: datetime
    asset: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


# 수익 거래
class IncomeTransactionCreate(TransactionBase):
    date: datetime
    type: str = "INCOME"
    asset_id: Optional[int] = None
    currency: str
    amount: float
    debit_account_id: int
    credit_account_id: int
    note: Optional[str] = None
    fees: Optional[Dict[str, Any]] = None
    

class IncomeTransactionResponse(IncomeTransactionCreate):
    id: int
    created_at: datetime
    asset: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True



# 4. 비용 거래
class ExpenseTransactionCreate(TransactionBase):
    type: str = "EXPENSE"
    asset_id: Optional[int] = None
    currency: str
    amount: float
    debit_account_id: int
    credit_account_id: int
    note: Optional[str] = None
    fees: Optional[Dict[str, Any]] = None

class ExpenseTransactionResponse(ExpenseTransactionCreate):
    id: int
    created_at: datetime
    asset: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


# 5. 손익 계산
class EstimatePLRequest(BaseModel):
    asset_id: int
    quantity: float
    price: float
    currency: str
    exchange_rate: float | None = None

class EstimatePLResponse(BaseModel):
    realized_profit_loss: float
    realized_details: list[Dict[str, Any]]


class Position(BaseModel):
    id: int
    quantity: float
    avg_price: float
    currency: str
    current_price: float
    last_updated: datetime
    position_metadata: Dict[str, Any]
    asset_id: int
    username: str
    asset: Optional[AssetBase]  # Asset 스키마로 변경
    
    class Config:
        from_attributes = True
    
    
class PositionResponse(BaseModel):
    items: List[Position]
    pagination: Pagination
    
    class Config:
        from_attributes = True


class TransactionAll(BaseModel):
    items: List[TransactionDict]
    pagination: Pagination

    class Config:
        from_attributes = True















