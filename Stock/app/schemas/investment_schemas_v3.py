from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime
from enum import Enum

class TradeType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class TransactionType(str, Enum):
    CASH = "CASH"
    ASSET = "ASSET"
    FEE = "FEE"
    DIVIDEND = "DIVIDEND"
    CURRENCY = "CURRENCY"

class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class BaseSchema(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class TransactionBase(BaseModel):
    date: datetime
    type: TransactionType
    currency: str
    amount: float = Field(gt=0, description="거래금액 (양수)")
    note: Optional[str] = None
    status: TransactionStatus = TransactionStatus.COMPLETED
    group_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase, BaseSchema):
    id: int

class CashTransactionBase(BaseModel):
    from_account_id: int
    to_account_id: int
    cash_type: str = Field(description="입금/출금/이체")
    reference_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class CashTransactionCreate(CashTransactionBase):
    transaction_id: Optional[int] = None

class CashTransaction(CashTransactionBase, BaseSchema):
    id: int
    transaction_id: int






class AssetTransactionBase(BaseModel):
    asset_id: int
    quantity: float = Field(gt=0, description="거래수량 (양수)")
    price: float = Field(gt=0, description="거래가격 (양수)")
    trade_type: TradeType = Field(description="매수/매도")
    broker: Optional[str] = None
    reference_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class AssetTransactionCreate(AssetTransactionBase):
    transaction_id: Optional[int] = None

class AssetTransaction(AssetTransactionBase):
    id: int
    transaction_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    
    

class FeeTransactionBase(BaseModel):
    fee_type: str = Field(description="매매수수료/기타수수료")
    amount: float = Field(gt=0, description="수수료금액 (양수)")
    reference_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class FeeTransactionCreate(FeeTransactionBase):
    transaction_id: Optional[int] = None

class FeeTransaction(FeeTransactionBase, BaseSchema):
    id: int
    transaction_id: int

class IncomeTransactionBase(BaseModel):
    asset_id: int
    income_type: str = Field(description="배당/이자/임대료 등")
    amount: float = Field(gt=0, description="수익금액 (양수)")
    tax_amount: float = Field(ge=0, description="원천징수세액")
    payment_date: datetime
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    reference_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class IncomeTransactionCreate(IncomeTransactionBase):
    transaction_id: Optional[int] = None

class IncomeTransaction(IncomeTransactionBase, BaseSchema):
    id: int
    transaction_id: int

# 복잡한 요청/응답 스키마
class TradeRequest(BaseModel):
    asset_transaction: AssetTransactionCreate
    cash_transaction: Optional[CashTransactionCreate] = None
    fee_transactions: Optional[List[FeeTransactionCreate]] = None

    model_config = ConfigDict(from_attributes=True)

class PositionResponse(BaseModel):
    position: "Position"
    asset: "Asset"
    latest_price: Optional["AssetPrice"] = None

    model_config = ConfigDict(from_attributes=True)

class PortfolioSummary(BaseModel):
    total_value: float = Field(ge=0, description="포트폴리오 총액")
    total_pl: float = Field(description="총 손익")
    positions: List[PositionResponse]

    model_config = ConfigDict(from_attributes=True)