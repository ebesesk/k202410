from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from app.db.base import Base

class BaseModel(Base):
    __abstract__ = True
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
    extra_data = Column(JSON, nullable=True)

class Account(BaseModel):
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    account_type = Column(String(20), nullable=False)  # ASSET, LIABILITY, EQUITY, INCOME, EXPENSE
    parent_id = Column(Integer, ForeignKey('accounts.id'), nullable=True)
    is_active = Column(Boolean, default=True)

    parent = relationship("Account", remote_side=[id], backref="children")

class Asset(BaseModel):
    __tablename__ = 'assets'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True)
    name = Column(String(100))
    asset_type = Column(String(50), nullable=False)  # STOCK, BOND, ETF, etc.
    currency = Column(String(10), nullable=False)
    is_active = Column(Boolean, default=True)

    prices = relationship("AssetPrice", backref="asset")
    positions = relationship("Position", backref="asset")
    transactions = relationship("AssetTransaction", backref="asset")

class AssetPrice(BaseModel):
    __tablename__ = 'asset_prices'
    
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('assets.id'))
    date = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)
    source = Column(String(50))

class Position(BaseModel):
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('assets.id'))
    quantity = Column(Float, default=0)
    avg_price = Column(Float, default=0)
    current_price = Column(Float)
    realized_pl = Column(Float, default=0)
    unrealized_pl = Column(Float, default=0)
    last_valuation_date = Column(DateTime)

class Transaction(BaseModel):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    transaction_type = Column(String(20), nullable=False)  # BUY, SELL, DIVIDEND, etc.
    currency = Column(String(10), nullable=False)
    amount = Column(Float, nullable=False)
    note = Column(String(500))
    status = Column(String(20), default='COMPLETED')  # PENDING, COMPLETED, CANCELLED
    group_id = Column(String(50))

    cash_transaction = relationship("CashTransaction", backref="transaction", uselist=False)
    asset_transaction = relationship("AssetTransaction", backref="transaction", uselist=False)
    fee_transaction = relationship("FeeTransaction", backref="transaction", uselist=False)
    income_transaction = relationship("IncomeTransaction", backref="transaction", uselist=False)

class CashTransaction(BaseModel):
    __tablename__ = 'cash_transactions'
    
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    account_id = Column(Integer, ForeignKey('accounts.id'))
    amount = Column(Float, nullable=False)
    
    account = relationship("Account", backref="cash_transactions")

class AssetTransaction(BaseModel):
    __tablename__ = 'asset_transactions'
    
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    asset_id = Column(Integer, ForeignKey('assets.id'))
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    
class FeeTransaction(BaseModel):
    __tablename__ = 'fee_transactions'
    
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    fee_type = Column(String(50))  # COMMISSION, TAX, etc.
    amount = Column(Float, nullable=False)

class IncomeTransaction(BaseModel):
    __tablename__ = 'income_transactions'
    
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    income_type = Column(String(50))  # DIVIDEND, INTEREST, etc.
    asset_id = Column(Integer, ForeignKey('assets.id'))
    amount = Column(Float, nullable=False)
    
    asset = relationship("Asset", backref="income_transactions")

class ExchangeRate(BaseModel):
    __tablename__ = 'exchange_rates'
    
    id = Column(Integer, primary_key=True)
    from_currency = Column(String(10), nullable=False)
    to_currency = Column(String(10), nullable=False)
    date = Column(DateTime, nullable=False)
    rate = Column(Float, nullable=False)
    source = Column(String(50))