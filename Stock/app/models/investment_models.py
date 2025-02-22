from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, JSON, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from app.db.base_class import Base

class Account(Base):
    """계정과목 - 확장 가능하도록 유연하게 설계"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20))           # 계정코드
    name = Column(String(100))          # 계정명
    category = Column(String(50))       # 자산/부채/자본/수익/비용
    type = Column(String(50))           # 세부유형
    is_active = Column(Boolean, default=True)
    account_metadata = Column(JSON)             # 추가 정보 저장용
    created_at = Column(DateTime, server_default=func.now())    # 생성일
    username = Column(String(50))

class Asset(Base):
    """자산 정보""" 
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(50))         # 종목코드/티커
    name = Column(String(100))          # 종목명
    type = Column(String(50))           # STOCK/ETF/CRYPTO 등
    currency = Column(String(10))       # 기준통화
    exchange = Column(String(50))       # 거래소/마켓
    sector = Column(String(100))        # 섹터/카테고리
    asset_metadata = Column(JSON)             # 추가 정보
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    username = Column(String(50))
    
    # 역참조 관계 설정
    positions = relationship("Position", back_populates="asset")

class Transaction(Base):
    """거래 내역"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    type = Column(String(50))           # BUY/SELL/DIVIDEND 등
    quantity = Column(Float)            # 수량
    price = Column(Float)               # 단가
    currency = Column(String(10))       # 거래통화
    exchange_rate = Column(Float)       # 환율
    amount = Column(Float)              # 거래금액
    transaction_metadata = Column(JSON)             # 추가 정보
    note = Column(String(500))          # 메모
    created_at = Column(DateTime, server_default=func.now())
    username = Column(String(50))
    fees = Column(JSON)                 # 수수료/세금 등 (확장가능)    
    # 복식부기 처리
    debit_account_id = Column(Integer, ForeignKey("accounts.id"))   # 차변 (借邊) - 자산의 증가, 비용의 발생
    credit_account_id = Column(Integer, ForeignKey("accounts.id"))   # 대변 (貸邊) - 부채/자본의 증가, 수익의 발생
    
    
     
    # 관계 설정
    asset = relationship("Asset", backref="transactions")
    debit_account = relationship("Account", foreign_keys=[debit_account_id], lazy='joined')     # 차변 (借邊) - 자산의 증가, 비용의 발생
    credit_account = relationship("Account", foreign_keys=[credit_account_id], lazy='joined')   # 대변 (貸邊) - 부 채/자본의 증가, 수익의 발생
    exchange_rates = relationship("ExchangeRate", back_populates="transaction")
    # fees = relationship("Fee", back_populates="transaction", cascade="all, delete-orphan")
    # cascade 옵션 설명
        # 1. `all`: 모든 연산(save-update, merge, refresh-expire, expunge, delete)을 전파
        # 2. `delete-orphan`: 부모 객체가 삭제될 때 자식 객체도 삭제
        # 3. `refresh-expire`: 부모 객체가 업데이트될 때 자식 객체도 업데이트
        # 4. `expunge`: 부모 객체가 삭제될 때 자식 객체도 삭제
        # 5. `delete`: 부모 객체가 삭제될 때 자식 객체도 삭제
    

class ExchangeRate(Base):
    """환율 정보"""
    __tablename__ = "exchange_rates"
    
    id = Column(Integer, primary_key=True)  # 고유 식별자   
    from_currency = Column(String(10))      # 원본 통화
    to_currency = Column(String(10))       # 대상 통화
    rate = Column(Float)                    # 환율 비율
    date = Column(DateTime)                  # 환율 적용일
    source = Column(String(50))             # 데이터 출처 (예: 환율 제공 기관)
    created_at = Column(DateTime, server_default=func.now())
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"))
    # 관계 설정
    transaction = relationship("Transaction", back_populates="exchange_rates")
    username = Column(String(50))

class Position(Base):
    """포지션 현황"""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    quantity = Column(Float)            # 보유수량
    avg_price = Column(Float)           # 평균단가
    currency = Column(String(10))       # 기준통화
    current_price = Column(Float)       # 현재가
    last_updated = Column(DateTime)     # 마지막 업데이트
    position_metadata = Column(JSON)             # 추가 정보
    asset = relationship("Asset")
    username = Column(String(50))
    
    # 정방향 관계 설정
    asset = relationship("Asset", back_populates="positions")



class CashBalance(Base):
    """현금 자산 관리"""
    __tablename__ = "cash_balances"
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    currency = Column(String(10))           # 통화
    balance = Column(Float)                 # 현재 잔액
    total_invested = Column(Float)          # 총 투자금액 (해당 통화)
    krw_invested = Column(Float)            # 원화 환산 투자금액
    cash_metadata = Column(JSON)            # 입출금 내역 등 추가 정보
    created_at = Column(DateTime, server_default=func.now())
    username = Column(String(50))

    
     
     

class Portfolio(Base):
    """포트폴리오 성과 분석"""
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    total_value = Column(Float)         # 총 자산 (KRW 기준)
    invested_value = Column(Float)      # 투자금액
    profit_loss = Column(Float)         # 손익
    portfolio_metadata = Column(JSON)    # 자산별 비중, 성과 분석 등
    created_at = Column(DateTime, server_default=func.now())
    username = Column(String(50))
