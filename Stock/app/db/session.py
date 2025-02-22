from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 기존 DB 엔진
engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 투자 관리 DB 엔진
investment_engine = create_engine(settings.INVESTMENT_DATABASE_URL, connect_args={"check_same_thread": False})
investment_session = sessionmaker(autocommit=False, autoflush=False, bind=investment_engine)

# 자산 관리 DB 엔진
asset_engine = create_engine(settings.ASSET_DATABASE_URL, connect_args={"check_same_thread": False})
AssetSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=asset_engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_investment_db():
    db = investment_session()
    try:
        yield db
    finally:
        db.close()

def get_asset_db():
    db = AssetSessionLocal()
    try:
        yield db
    finally:
        db.close()