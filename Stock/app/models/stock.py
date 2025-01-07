from sqlalchemy import Column, String, Float, Integer, Index, UniqueConstraint, JSON
from app.db.base_class import Base

class Stocks(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    shcode = Column(String(50), nullable=False, unique=True)
    shname = Column(String(100), nullable=False)
    gubun = Column(String(50), nullable=False)
    ETFgubun = Column(String(50), nullable=False)
    
class InterestStock(Base):
    __tablename__ = "interest_stock"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    종목코드 = Column(String(50), nullable=False)
    한글기업명 = Column(String(100), nullable=False)
    시장구분 = Column(String(50), nullable=False)
    업종구분명 = Column(String(50), nullable=False)
    tag = Column(String(200), nullable=True)
    username = Column(String(100), nullable=False)  # OAuth 사용자 ID
    # 인덱스 추가
    __table_args__ = (
        Index('idx_username', username),  # 단일 컬럼 인덱스
        Index('idx_username_stock', username, 종목코드),  # 복합 인덱스
        Index('idx_tag', tag),  # tag 검색을 위한 인덱스
    )

class AppKey(Base):
    __tablename__ = "app_key"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cname = Column(String(100), nullable=False)
    appkey = Column(String(200), nullable=False)
    appsecretkey = Column(String(200), nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    # 복합 unique 제약조건 추가
    __table_args__ = (
        UniqueConstraint('cname', 'username', name='uix_cname_username'),
    )

# class ChartData(Base):
#     __tablename__ = "chart_data"
    
#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     chart_data = Column(JSON, nullable=False)
#     date = Column(String(50), nullable=False)
#     period = Column(String(50), nullable=False)
#     shcode = Column(String(50), nullable=False)
#     username = Column(String(100), nullable=False)
#     __table_args__ = (
#         Index('idx_username', username),  # 단일 컬럼 인덱스
#         Index('idx_username_shcode', username, shcode),  # 복합 인덱스
#     )