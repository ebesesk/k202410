# app/api/v1/endpoints/investment.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any

from app.utils.dependencies import get_current_user
from app.schemas import investment_schemas
from app.crud import investment as crud_investment
from app.models import investment_models
from app.db.session import investment_session
from app.core.config import settings
import traceback
base_accounts = settings.BASE_ACCOUNTS


router = APIRouter()

# DB 의존성
def get_investment_db():
    db = investment_session()
    try:
        yield db
    finally:
        db.close()


@router.post("/transactions", response_model=investment_schemas.TransactionResponse) # 거래 내역 생성
def create_transaction(
        transaction: investment_schemas.TransactionCreate,
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)
    ):
    """거래 내역 생성"""
    username = current_user['username']
    transaction.username = username
    try:
        if transaction.type in ["DEPOSIT", "WITHDRAW"]: 
            # 참조 데이터 확인
            is_valid, error_message = crud_investment.verify_transaction_references(
                    db=db,
                    transaction_type=transaction.type,
                    asset_id=transaction.asset_id,
                    debit_account_id=transaction.debit_account_id,
                    credit_account_id=transaction.credit_account_id,
                )

            
            if not is_valid:
                raise HTTPException(status_code=404, detail=error_message)

            return crud_investment.create_transaction(db, transaction)
        elif transaction.type == "EXCHANGE":
             # 환전 거래 데이터 변환
            transaction_data = {
                "date": transaction.date,
                "type": transaction.type,
                "currency": transaction.from_currency,
                "amount": transaction.from_amount,
                "exchange_rate": transaction.exchange_rate,
                "debit_account_id": transaction.debit_account_id,
                "credit_account_id": transaction.credit_account_id,
                "fees": transaction.fees,
                "note": transaction.note,
                "username": username,
                "transaction_metadata": {
                    "to_currency": transaction.to_currency,
                    "to_amount": transaction.to_amount
                }
            }
            transaction = investment_schemas.TransactionCreate(**transaction_data)
            
            # 환전 거래 처리
            is_valid, error_message = crud_investment.verify_exchange_transaction(
                db=db,
                transaction=transaction
            )
            
            if not is_valid:
                raise HTTPException(status_code=404, detail=error_message)
                
            # 거래 생성 및 관련 데이터 업데이트
            result = crud_investment.create_exchange_transaction(
                db=db,
                transaction=transaction,
                username=username
            )
            
            return result
        
        
    except Exception as e:
        error_detail = {
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        print("상세 에러 정보:", error_detail)
        raise HTTPException(
            status_code=500, 
            detail=f"거래 생성 중 오류 발생: {str(e)}\n{traceback.format_exc()}"
        )

@router.get("/transactions", response_model=investment_schemas.TransactionListResponse)
def read_transactions(
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = Query(None),
        end_date: Optional[datetime] = Query(None),
        transaction_type: Optional[str] = Query(None),
        asset_id: Optional[int] = Query(None),
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)
    ):
    """거래 내역 조회"""
    username = current_user['username']
    transactions = crud_investment.get_transactions(
        db, 
        username=username,
        skip=skip, 
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type,
        asset_id=asset_id,
    )
    return transactions

@router.get("/transactions/{transaction_id}", response_model=investment_schemas.TransactionResponse)
def read_transaction(
        transaction_id: int,
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)
    ):
    """특정 거래 내역 조회"""
    username = current_user['username']
    transaction = crud_investment.get_transaction(db, transaction_id, username)
    if not transaction:
        raise HTTPException(status_code=404, detail="거래 내역을 찾을 수 없습니다")
    return transaction

@router.put("/transactions/{transaction_id}", response_model=investment_schemas.TransactionResponse)
def update_transaction(
        transaction_id: int,
        transaction_update: investment_schemas.TransactionCreate, 
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)
    ):
    """거래 내역 수정"""
    username = current_user['username']
    transaction_update.username = username
    db_transaction = crud_investment.get_transaction(db, transaction_id, username)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="거래 내역을 찾을 수 없습니다")
    
    try:
        return crud_investment.update_transaction(db, db_transaction, transaction_update)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"거래 수정 중 오류 발생: {str(e)}")

@router.delete("/transactions/{transaction_id}")
def delete_transaction(
        transaction_id: int,
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)
    ):
    """거래 내역 삭제"""
    username = current_user['username']
    db_transaction = crud_investment.get_transaction(db, transaction_id, username)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="거래 내역을 찾을 수 없습니다")
    
    try:
        crud_investment.delete_transaction(db, db_transaction)
        return {"message": "거래 내역이 삭제되었습니다"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"거래 삭제 중 오류 발생: {str(e)}")

@router.get("/transactions/summary", response_model=List[Dict[str, Any]])
def get_transaction_summary(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)
    ):
    """거래 유형별 요약 정보 조회"""
    username = current_user['username']
    return crud_investment.get_transaction_summary(db, username, start_date, end_date)




@router.post("/assets", response_model=investment_schemas.Asset)
def create_asset(
        asset: investment_schemas.AssetCreate,
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)
    ):
    """자산 생성"""
    print('create_asset:', asset)
    username = current_user['username']
    asset.username = username
    return crud_investment.create_asset(db, asset)

@router.get("/assets", response_model=investment_schemas.AssetListResponse)
def read_assets(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)
    ):
    """자산 목록 조회"""
    username = current_user['username']
    assets, total_items = crud_investment.get_assets(db, username, skip, limit)
    return {
        "items": assets,
        "pagination": {
            "currentPage": skip // limit + 1,
            "itemsPerPage": limit,
            "totalItems": total_items,
            "totalPages": (total_items + limit - 1) // limit
        }
    }

@router.get("/assets/{asset_id}", response_model=investment_schemas.Asset)
def read_asset(
        asset_id: int,
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)
    ):
    """특정 자산 조회"""
    username = current_user['username']
    asset = crud_investment.get_assets(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="자산을 찾을 수 없습니다")
    return asset

@router.put("/assets/{asset_id}", response_model=investment_schemas.Asset)
def update_asset(
        asset_id: int,
        asset_update: investment_schemas.AssetCreate,
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)
    ):
    """자산 정보 수정"""
    username = current_user['username']
    asset_update.username = username
    return crud_investment.update_asset(db, asset_id, asset_update)

@router.delete("/assets/{asset_id}")
def delete_asset(
        asset_id: int,
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)
    ):
    """자산 삭제"""
    username = current_user['username']
    return crud_investment.delete_asset(db, asset_id, username)

@router.post("/assets/initialize/stocks", response_model=List[investment_schemas.Asset])
def initialize_stocks(
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)    
    ):
    """주요 주식 종목 초기화"""
    username = current_user['username']
    try:
        # 기본 주식 종목 데이터
        default_stocks = [
            {
                "symbol": "005930",
                "name": "삼성전자",
                "type": "stock",
                "currency": "KRW",
                "exchange": "KOSPI",
                "sector": "전기전자",
                "username": username,
                "asset_metadata": {
                    "market_cap": "500조",
                    "industry": "반도체/가전",
                    "listing_date": "1975-06-11",
                    "website": "www.samsung.com",
                    "products": ["반도체", "스마트폰", "가전제품"]
                }
            },
            {
                "symbol": "207940",
                "name": "삼성바이오로직스",
                "type": "stock",
                "currency": "KRW",
                "exchange": "KOSPI",
                "sector": "의약품",
                "username": username,
                "asset_metadata": {
                    "market_cap": "50조",
                    "industry": "바이오/제약",
                    "listing_date": "2016-11-10",
                    "business_areas": ["바이오시밀러", "CMO"],
                    "facilities": ["송도 1공장", "송도 2공장", "송도 3공장"]
                }
            },
            {
                "symbol": "263750.KQ",  # .KQ는 KOSDAQ
                "name": "펄어비스",
                "type": "stock",       # KOSDAQ 종목
                "currency": "KRW",
                "exchange": "KOSDAQ",
                "sector": "소프트웨어",
                "username": username,
                "asset_metadata": {
                    "market_cap": "10조",
                    "industry": "게임/소프트웨어",
                    "listing_date": "2017-09-14",
                    "website": "www.pearlabyss.com",
                    "products": ["게임", "소프트웨어"]
                }
            },
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "type": "stock",
                "currency": "USD",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "username": username,
                "asset_metadata": {
                    "market_cap": "3T USD",
                    "industry": "Consumer Electronics",
                    "listing_date": "1980-12-12",
                    "headquarters": "Cupertino, California",
                    "products": ["iPhone", "Mac", "iPad", "Services"]
                }
            },
            # 암호화폐
            {
                "symbol": "BTC-USD",  # Coinbase 형식
                "name": "Bitcoin",
                "type": "crypto",
                "currency": "USD",
                "exchange": "COINBASE",  # 또는 "BINANCE", "UPBIT" 등
                "sector": "Cryptocurrency",
                "username": username,
                "description": "가장 큰 시가총액의 암호화폐",
                "asset_metadata": {
                    "decimal_places": 8,
                    "network": "Bitcoin",
                    "max_supply": "21000000"
                }
            },
            {
                "symbol": "ETH-USD",
                "name": "Ethereum",
                "type": "crypto",
                "currency": "USD",
                "exchange": "COINBASE",
                "sector": "Cryptocurrency",
                "username": username,
                "description": "스마트 컨트랙트 플랫폼",
                "asset_metadata": {
                    "decimal_places": 18,
                    "network": "Ethereum",
                    "token_type": "Native"
                }
            },
            {
                "symbol": "KRW-BTC",  # 업비트 형식
                "name": "비트코인",
                "type": "crypto",
                "currency": "KRW",
                "exchange": "UPBIT",
                "sector": "Cryptocurrency",
                "username": username,
                "description": "비트코인 원화 마켓",
                "asset_metadata": {
                    "market_type": "KRW",
                    "english_name": "Bitcoin",
                    "original_symbol": "BTC"
                }
            },
            
        ]

        created_assets = []
        for stock in default_stocks:
            # 이미 존재하는 종목인지 확인
            existing_asset = crud_investment.get_asset_by_symbol(db, stock["symbol"], username)
            if not existing_asset:
                asset_schema = investment_schemas.AssetCreate(**stock)
                print('asset_schema:', asset_schema)
                created_asset = crud_investment.create_asset(db, asset_schema)
                created_assets.append(created_asset)

        return created_assets
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"주식 초기화 중 오류 발생: {str(e)}"
        )







@router.post("/accounts/initialize/{category}", response_model=List[investment_schemas.Account])
def initialize_category_accounts(
        category: str,
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)
    ):
    """특정 카테고리의 계정과목 초기화"""
    username = current_user['username']
    if category not in base_accounts:
        raise HTTPException(
            status_code=400,
            detail=f"유효하지 않은 카테고리입니다. 가능한 카테고리: {', '.join(base_accounts.keys())}"
        )

    try:
        created_accounts = crud_investment.initialize_category_accounts(db, category, base_accounts, username)
        return created_accounts
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"계정 초기화 중 오류 발생: {str(e)}"
        )

@router.post("/accounts/initialize-all", response_model=List[investment_schemas.Account])
def initialize_all_accounts(
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)
    ):
    """모든 카테고리의 계정과목 초기화"""
    username = current_user['username']
    try:
        created_accounts = crud_investment.initialize_all_accounts(db, base_accounts, username)
        return created_accounts
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"계정 초기화 중 오류 발생: {str(e)}"
        )

@router.post("/accounts", response_model=investment_schemas.Account)
def create_account(
        account: investment_schemas.AccountCreate,
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)
    ):
    username = current_user['username']
    account.username = username
    return crud_investment.create_account(db, account)

@router.put("/accounts/{account_id}", response_model=investment_schemas.Account)
def update_account(
        account_id: int,
        account_update: investment_schemas.AccountUpdate,
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)
    ):
    username = current_user['username']
    # account_update.username = username
    try:
        return crud_investment.update_account(db, account_id, account_update, username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"계정 수정 중 오류 발생: {str(e)}")

@router.get("/accounts", response_model=investment_schemas.AccountListResponse)
def read_accounts(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)
    ):
    username = current_user['username']
    accounts = db.query(investment_models.Account)\
        .filter(investment_models.Account.username == username)\
        .order_by(investment_models.Account.code)\
        .offset(skip)\
        .limit(limit)\
        .all()
    total_items = db.query(investment_models.Account)\
        .filter(investment_models.Account.username == username)\
        .count()
    return {
        "items": accounts,
        "pagination": {
            "currentPage": skip // limit + 1,
            "itemsPerPage": limit,
            "totalItems": total_items,
            "totalPages": (total_items + limit - 1) // limit
        }
    }

@router.get("/accounts/{account_id}", response_model=investment_schemas.Account)
def read_account_by_id(
        account_id: int,
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)
    ):
    username = current_user['username']
    account = crud_investment.get_account_by_id(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="계정을 찾을 수 없습니다")
    return account




@router.get("/positions", response_model=List[investment_schemas.Position])
def get_positions(
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)
    ):
    """포지션 현황 조회"""
    try:
        username = current_user['username']
        positions = crud_investment.get_positions(db, username=username)
        return positions
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"포지션 조회 중 오류 발생: {str(e)}"
        )

@router.get("/positions/{asset_id}", response_model=investment_schemas.Position)
def get_position_by_asset(
        asset_id: int,
        db: Session = Depends(get_investment_db),
        current_user = Depends(get_current_user)
    ):
    """특정 자산의 포지션 조회"""
    try:
        username = current_user['username']
        position = crud_investment.get_position_by_asset(
            db, 
            asset_id=asset_id, 
            username=username
        )
        if not position:
            raise HTTPException(
                status_code=404, 
                detail=f"자산 ID {asset_id}에 대한 포지션을 찾을 수 없습니다."
            )
        return position
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"포지션 조회 중 오류 발생: {str(e)}"
        )





# 환율 생성
@router.post("/exchange-rates/", response_model=investment_schemas.ExchangeRateResponse)
def create_exchange_rate(
    exchange_rate: investment_schemas.ExchangeRateCreate,
    db: Session = Depends(get_investment_db)
):
    return crud_investment.create_exchange_rate(db=db, exchange_rate=exchange_rate)

# 환율 목록 조회
@router.get("/exchange-rates/", response_model=List[investment_schemas.ExchangeRateResponse])
def get_exchange_rates(
    skip: int = 0,
    limit: int = 100,
    from_currency: Optional[str] = None,
    to_currency: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    transaction_id: Optional[int] = None,
    db: Session = Depends(get_investment_db)
):
    return crud_investment.get_exchange_rates(
        db, skip=skip, limit=limit,
        from_currency=from_currency,
        to_currency=to_currency,
        start_date=start_date,
        end_date=end_date,
        transaction_id=transaction_id
    )

# 특정 환율 조회
@router.get("/exchange-rates/{exchange_rate_id}", response_model=investment_schemas.ExchangeRateResponse)
def get_exchange_rate(
    exchange_rate_id: int,
    db: Session = Depends(get_investment_db)
):
    exchange_rate = crud_investment.get_exchange_rate(db, exchange_rate_id=exchange_rate_id)
    if exchange_rate is None:
        raise HTTPException(status_code=404, detail="Exchange rate not found")
    return exchange_rate

# 특정 거래의 환율 목록 조회
@router.get("/transactions/{transaction_id}/exchange-rates/", response_model=List[investment_schemas.ExchangeRateResponse])
def get_transaction_exchange_rates(
    transaction_id: int,
    db: Session = Depends(get_investment_db)
):
    exchange_rates = crud_investment.get_exchange_rates_by_transaction(
        db, transaction_id=transaction_id
    )
    return exchange_rates

# 환율 삭제
@router.delete("/exchange-rates/{exchange_rate_id}")
def delete_exchange_rate(
    exchange_rate_id: int,
    db: Session = Depends(get_investment_db)
):
    success = crud_investment.delete_exchange_rate(db, exchange_rate_id=exchange_rate_id)
    if not success:
        raise HTTPException(status_code=404, detail="Exchange rate not found")
    return {"message": "Exchange rate deleted successfully"}

