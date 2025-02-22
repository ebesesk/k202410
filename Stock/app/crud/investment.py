from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.models import investment_models
from app.schemas import investment_schemas

def create_transaction(db: Session, transaction: investment_schemas.TransactionCreate):
    """거래 내역 생성"""
    try:
        print('transaction.type:', transaction.type)
        # 현금 입출금 처리
        if transaction.type in ["DEPOSIT", "WITHDRAW"]:  # 현금 입출금
            portfolio = get_or_create_portfolio(db, transaction.username)
            
            if transaction.type == "DEPOSIT":  # 입금
                portfolio.cash_value = (portfolio.cash_value or 0) + transaction.amount
                portfolio.total_value = (portfolio.total_value or 0) + transaction.amount
            else:  # 출금
                portfolio.cash_value = (portfolio.cash_value or 0) - transaction.amount
                portfolio.total_value = (portfolio.total_value or 0) - transaction.amount
            
            portfolio.date = transaction.date
            db.commit()
            db.refresh(portfolio)

        
        # 환전 거래 처리
        elif transaction.type == "EXCHANGE":
            pass
        
        # 기존 매수/매도 로직...
        elif transaction.type in ["BUY", "SELL"]:
            # ... 기존 포지션 업데이트 코드 ...
            
            # 포트폴리오 현금 업데이트
            portfolio = get_or_create_portfolio(db, transaction.username)
            total_amount = transaction.quantity * transaction.price
            
            if transaction.type == "BUY":
                portfolio.cash_value = (portfolio.cash_value or 0) - total_amount
                portfolio.invested_value = (portfolio.invested_value or 0) + total_amount
            else:  # SELL
                portfolio.cash_value = (portfolio.cash_value or 0) + total_amount
                portfolio.invested_value = (portfolio.invested_value or 0) - total_amount
            
            portfolio.date = transaction.date
            db.commit()
            db.refresh(portfolio)

        # 거래 내역 생성
        db_transaction = investment_models.Transaction(**transaction.model_dump())
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        
        return db_transaction
    except Exception as e:
        db.rollback()
        raise e

def update_transaction(
        db: Session,
        transaction_id: int,
        transaction_update: investment_schemas.TransactionCreate
    ) -> investment_models.Transaction:
    """거래 내역 수정"""
    try:
        # 기존 거래 조회
        old_transaction = db.query(investment_models.Transaction).filter(
            investment_models.Transaction.id == transaction_id
        ).first()
        
        if not old_transaction:
            raise HTTPException(status_code=404, detail="거래를 찾을 수 없습니다")
        
        # 기존 거래 취소 처리
        if old_transaction.type in ["DEPOSIT", "WITHDRAW"]:
            portfolio = get_or_create_portfolio(db, old_transaction.username)
            if old_transaction.type == "DEPOSIT":
                portfolio.cash_value = (portfolio.cash_value or 0) - old_transaction.amount
                portfolio.total_value = (portfolio.total_value or 0) - old_transaction.amount
            else:  # WITHDRAW
                portfolio.cash_value = (portfolio.cash_value or 0) + old_transaction.amount
                portfolio.total_value = (portfolio.total_value or 0) + old_transaction.amount
        
        elif old_transaction.type in ["BUY", "SELL"]:
            portfolio = get_or_create_portfolio(db, old_transaction.username)
            old_amount = old_transaction.quantity * old_transaction.price
            if old_transaction.type == "BUY":
                portfolio.cash_value = (portfolio.cash_value or 0) + old_amount
                portfolio.invested_value = (portfolio.invested_value or 0) - old_amount
            else:  # SELL
                portfolio.cash_value = (portfolio.cash_value or 0) - old_amount
                portfolio.invested_value = (portfolio.invested_value or 0) + old_amount
        
        # 새로운 거래 정보로 업데이트
        for field, value in transaction_update.model_dump().items():
            setattr(old_transaction, field, value)
        
        # 새로운 거래 처리
        if transaction_update.type in ["DEPOSIT", "WITHDRAW"]:
            if transaction_update.type == "DEPOSIT":
                portfolio.cash_value = (portfolio.cash_value or 0) + transaction_update.amount
                portfolio.total_value = (portfolio.total_value or 0) + transaction_update.amount
            else:  # WITHDRAW
                portfolio.cash_value = (portfolio.cash_value or 0) - transaction_update.amount
                portfolio.total_value = (portfolio.total_value or 0) - transaction_update.amount
            
        elif transaction_update.type in ["BUY", "SELL"]:
            new_amount = transaction_update.quantity * transaction_update.price
            if transaction_update.type == "BUY":
                portfolio.cash_value = (portfolio.cash_value or 0) - new_amount
                portfolio.invested_value = (portfolio.invested_value or 0) + new_amount
            else:  # SELL
                portfolio.cash_value = (portfolio.cash_value or 0) + new_amount
                portfolio.invested_value = (portfolio.invested_value or 0) - new_amount
        
        portfolio.date = transaction_update.date
        db.commit()
        db.refresh(old_transaction)
        db.refresh(portfolio)
        
        # 포트폴리오 총 가치 업데이트
        update_portfolio_total_value(db, old_transaction.username)
        
        return old_transaction
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"거래 수정 중 오류 발생: {str(e)}")

def delete_transaction(db: Session, transaction: investment_models.Transaction) -> bool:
    """거래 내역 삭제"""
    try:
        # 포트폴리오 업데이트
        if transaction.type in ["DEPOSIT", "WITHDRAW"]:
            portfolio = get_or_create_portfolio(db, transaction.username)
            if transaction.type == "DEPOSIT":
                portfolio.cash_value = (portfolio.cash_value or 0) - transaction.amount
                portfolio.total_value = (portfolio.total_value or 0) - transaction.amount
            else:  # WITHDRAW
                portfolio.cash_value = (portfolio.cash_value or 0) + transaction.amount
                portfolio.total_value = (portfolio.total_value or 0) + transaction.amount
            
        elif transaction.type in ["BUY", "SELL"]:
            portfolio = get_or_create_portfolio(db, transaction.username)
            amount = transaction.quantity * transaction.price
            if transaction.type == "BUY":
                portfolio.cash_value = (portfolio.cash_value or 0) + amount
                portfolio.invested_value = (portfolio.invested_value or 0) - amount
            else:  # SELL
                portfolio.cash_value = (portfolio.cash_value or 0) - amount
                portfolio.invested_value = (portfolio.invested_value or 0) + amount
        
        db.delete(transaction)
        db.commit()
        
        # 포트폴리오 총 가치 업데이트
        update_portfolio_total_value(db, transaction.username)
        
        return True
    except Exception as e:
        db.rollback()
        raise e

def get_transaction(db: Session, transaction_id: int, username: str) -> Optional[investment_models.Transaction]:
    """특정 거래 내역 조회"""
    return db.query(investment_models.Transaction).filter(
        investment_models.Transaction.id == transaction_id,
        investment_models.Transaction.username == username
    ).first()

def get_transactions(
        db: Session, 
        username: str,
        skip: int = 0, 
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[str] = None,
        asset_id: Optional[int] = None
    ) -> List[investment_models.Transaction]:
    """거래 내역 조회"""
    query = db.query(investment_models.Transaction)
    
    # 필터 적용
    query = query.filter(investment_models.Transaction.username == username)
    if start_date:
        query = query.filter(investment_models.Transaction.date >= start_date)
    if end_date:
        query = query.filter(investment_models.Transaction.date <= end_date)
    if transaction_type:
        query = query.filter(investment_models.Transaction.type == transaction_type)
    if asset_id:
        query = query.filter(investment_models.Transaction.asset_id == asset_id)

    
    # 전체 아이템 수 계산
    total_items = query.count()
    
    # 정렬 (최신 거래순)
    query = query.order_by(investment_models.Transaction.date.desc())
    
    # 페이지네이션 적용
    transactions = query.offset(skip).limit(limit).all()
    
    # 페이지네이션 정보 포함하여 반환
    return {
        "items": transactions,
        "pagination": {
            "currentPage": skip // limit + 1,
            "itemsPerPage": limit,
            "totalItems": total_items,
            "totalPages": (total_items + limit - 1) // limit
        }
    }

def get_transaction_summary(
        db: Session,
        username: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
    """거래 유형별 요약 정보 조회"""
    query = db.query(
        investment_models.Transaction.type,
        func.count().label('count'),
        func.sum(investment_models.Transaction.amount).label('total_amount')
    ).filter(investment_models.Transaction.username == username).group_by(investment_models.Transaction.type)
    
    if start_date:
        query = query.filter(investment_models.Transaction.date >= start_date)
    if end_date:
        query = query.filter(investment_models.Transaction.date <= end_date)
    
    summaries = query.all()
    return [
        {
            "type": summary.type,
            "count": summary.count,
            "total_amount": float(summary.total_amount) if summary.total_amount else 0
        }
        for summary in summaries
    ]

def verify_transaction_references(
        db: Session,
        transaction_type: str,
        asset_id: int,
        debit_account_id: int,
        credit_account_id: int,
    ) -> tuple[bool, Optional[str]]:
    """거래 관련 참조 데이터 확인"""
    if transaction_type != 'DEPOSIT' and transaction_type != 'WITHDRAWAL':
        # 자산 확인
        asset = db.query(investment_models.Asset).filter(
            investment_models.Asset.id == asset_id
        ).first()
        if not asset:
            return False, "자산을 찾을 수 없습니다"

    # 차변 계정 확인
    debit_account = db.query(investment_models.Account).filter(
        investment_models.Account.id == debit_account_id
    ).first()
    if not debit_account:
        return False, "차변 계정을 찾을 수 없습니다"

    # 대변 계정 확인
    credit_account = db.query(investment_models.Account).filter(
        investment_models.Account.id == credit_account_id
    ).first()
    if not credit_account:
        return False, "대변 계정을 찾을 수 없습니다"
    
    # # 사용자 확인
    # if credit_account.username != username:
    #     return False, "대변 계정의 사용자가 일치하지 않습니다"

    return True, None



def get_or_create_portfolio(db: Session, username: str):
    """포트폴리오 조회 또는 생성"""
    portfolio = db.query(investment_models.Portfolio).filter(
        investment_models.Portfolio.username == username
    ).first()
    
    if not portfolio:
        portfolio = investment_models.Portfolio(
            username=username,
            date=datetime.now(),
            total_value=0,
            cash_value=0,
            invested_value=0,
            profit_loss=0,
            portfolio_metadata={}
        )
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
    
    return portfolio

def update_portfolio_total_value(db: Session, username: str):
    """포트폴리오 총 자산 가치 업데이트"""
    portfolio = get_or_create_portfolio(db, username)
    
    # 모든 포지션의 현재 가치 계산
    positions = db.query(investment_models.Position).filter(
        investment_models.Position.username == username
    ).all()
    
    position_value = sum(
        position.quantity * position.current_price 
        for position in positions
    )
    
    # 총 자산 = 포지션 가치 + 현금
    portfolio.total_value = position_value + (portfolio.cash_value or 0)
    # 손익 = 총 자산 - 투자금액
    portfolio.profit_loss = portfolio.total_value - (portfolio.invested_value or 0)
    portfolio.date = datetime.now()
    
    db.commit()
    db.refresh(portfolio)
    return portfolio

    


def get_positions(db: Session, username: str):
    """사용자의 모든 포지션 조회"""
    return db.query(investment_models.Position)\
        .filter(investment_models.Position.username == username)\
        .all()

def get_position_by_asset(db: Session, asset_id: int, username: str):
    """특정 자산의 포지션 조회"""
    return db.query(investment_models.Position)\
        .filter(
            investment_models.Position.asset_id == asset_id,
            investment_models.Position.username == username
        )\
        .first()

def calculate_positions(db: Session, username: str):
    """사용자의 포지션 계산"""
    # 모든 거래내역을 가져와서 자산별로 집계
    positions = db.query(
        investment_models.Transaction.asset_id,
        investment_models.Asset.name.label('asset_name'),
        investment_models.Asset.type.label('asset_type'),
        investment_models.Asset.currency,
        func.sum(investment_models.Transaction.quantity).label('total_quantity'),
        func.sum(investment_models.Transaction.amount).label('total_amount'),
        # 평균 단가 계산
        (func.sum(investment_models.Transaction.amount) / func.sum(investment_models.Transaction.quantity)).label('average_price')
    ).join(
        investment_models.Asset,
        investment_models.Transaction.asset_id == investment_models.Asset.id
    ).filter(
        investment_models.Transaction.username == username,
        investment_models.Asset.type.in_(['STOCK', 'ETF', 'FUND', 'CRYPTO'])  # 포지션 계산이 필요한 자산 유형
    ).group_by(
        investment_models.Transaction.asset_id,
        investment_models.Asset.name,
        investment_models.Asset.type,
        investment_models.Asset.currency
    ).having(
        func.sum(investment_models.Transaction.quantity) != 0  # 수량이 0이 아닌 포지션만
    ).all()

    return positions



def initialize_category_accounts(
        db: Session, category: str, 
        base_accounts: Dict, 
        username: str
    ) -> List[investment_models.Account]:
    
    """특정 카테고리의 계정과목 초기화"""
    if category not in base_accounts:
        return []

    created_accounts = []
    category_accounts = base_accounts[category]
    
    # 각 계정 유형별로 처리
    for account_type, accounts in category_accounts.items():
        for account_data in accounts:
            # 계정 분류(category) 추가
            
            if account_type == "assets":
                account_data["category"] = "자산"
            elif account_type == "liabilities":
                account_data["category"] = "부채"
            elif account_type == "equity":
                account_data["category"] = "자본"
            elif account_type == "expenses":
                account_data["category"] = "비용"
            elif account_type == "income":
                account_data["category"] = "수익"
            
            account_data["username"] = username
            account_data["is_active"] = True
            
            # 기존 계정 확인
            existing = db.query(investment_models.Account).filter(
                investment_models.Account.code == account_data["code"],
                investment_models.Account.username == username
            ).first()
            
            if not existing:
                account = investment_models.Account(**account_data)
                db.add(account)
                created_accounts.append(account)
    
    db.commit()
    
    # refresh all accounts
    for account in created_accounts:
        db.refresh(account)
    
    return created_accounts

def initialize_all_accounts(db: Session, base_accounts: Dict, username: str) -> List[investment_models.Account]:
    """모든 카테고리의 계정과목 초기화"""
    created_accounts = []
    for category in base_accounts.keys():
        accounts = initialize_category_accounts(db, category, base_accounts, username)
        created_accounts.extend(accounts)
    return created_accounts

def update_account(
        db: Session, account_id: int, 
        account_update: investment_schemas.AccountCreate,
        username
    ) -> investment_models.Account:
    """계정 정보 수정"""
    
    account = db.query(investment_models.Account).filter(
        investment_models.Account.id == account_id,
        investment_models.Account.username == username
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="계정을 찾을 수 없습니다")
    
    for key, value in account_update.model_dump().items():
        setattr(account, key, value)
    
    db.commit()
    db.refresh(account)
    return account

def get_account_by_id(
        db: Session, 
        account_id: int
    ) -> Optional[investment_models.Account]:
    """계정 아이디로 계정 조회"""
    return db.query(investment_models.Account).filter(
        investment_models.Account.id == account_id
    ).first()

def create_account(db: Session, account: investment_schemas.AccountCreate) -> investment_models.Account:
    """계정 생성"""
    # 존재 여부 확인
    existing = db.query(investment_models.Account).filter(
        investment_models.Account.code == account.code,
        investment_models.Account.username == account.username
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 계정입니다")
    
    db_account = investment_models.Account(**account.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account





def get_assets(
        db: Session,
        username: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[investment_models.Asset]:
    """자산 목록 조회 - username 일치 또는 username이 없는 것만"""
    
    assets = db.query(investment_models.Asset).filter(
        investment_models.Asset.username == username
    ).offset(skip).limit(limit).all()
    total_items = db.query(investment_models.Asset).filter(
        investment_models.Asset.username == username
    ).count()
    return assets, total_items
    # return {
    #     "items": assets,
    #     "pagination": {
    #         "currentPage": skip // limit + 1,
    #         "itemsPerPage": limit,
    #         "totalItems": total_items,
    #         "totalPages": (total_items + limit - 1) // limit
    #     }
    # }
    
    
def get_asset(
        db: Session,
        asset_id: int
    ) -> Optional[investment_models.Asset]:
    """특정 자산 조회"""
    return db.query(investment_models.Asset).filter(
        investment_models.Asset.id == asset_id
    ).first()

def update_asset(
        db: Session,
        asset_id: int,
        asset_update: investment_schemas.AssetCreate
    ) -> investment_models.Asset:
    """자산 정보 수정"""
    db_asset = get_asset(db, asset_id)
    if not db_asset:
        raise HTTPException(status_code=404, detail="자산을 찾을 수 없습니다")
    
    try:
        for key, value in asset_update.dict().items():
            setattr(db_asset, key, value)
        db.commit()
        db.refresh(db_asset)
        return db_asset
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"자산 수정 중 오류 발생: {str(e)}")

def delete_asset(db: Session, asset_id: int, username: str) -> dict:
    """자산 삭제"""
    db_asset = get_asset(db, asset_id)
    if not db_asset:
        raise HTTPException(status_code=404, detail="자산을 찾을 수 없습니다")
    
    if db_asset.username != username:
        raise HTTPException(status_code=403, detail="자산의 소유자가 일치하지 않습니다")
    
    try:
        db.delete(db_asset)
        db.commit()
        return {"message": "자산이 삭제되었습니다"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"자산 삭제 중 오류 발생: {str(e)}")
    
def get_asset_by_symbol(db: Session, symbol: str, username: Optional[str] = None):
    """코목코드/티커로 자산 조회"""
    return db.query(investment_models.Asset).filter(
        investment_models.Asset.symbol == symbol,
        investment_models.Asset.username == username
    ).first()

def create_asset(db: Session, asset: investment_schemas.AssetCreate):
    """자산 생성"""
    print('create_asset:', asset.type)
    is_stock = asset.type == 'STOCK' or asset.type == 'ETF' or asset.type == 'FUND' or asset.type == 'BOND' or asset.type == 'CRYPTO'
    if is_stock and get_asset_by_symbol(db, asset.symbol, asset.username):
        raise HTTPException(status_code=400, detail="이미 존재하는 자산입니다")
    db_asset = investment_models.Asset(**asset.model_dump())
    try:
        db.add(db_asset)
        db.commit()
        db.refresh(db_asset)
        return db_asset
    except Exception as e:
        db.rollback()
        raise e




def create_exchange_rate(
        db: Session,
        transaction_id: int,
        currency: str,
        exchange_rate: float,
        date: datetime,
        source: str = "MANUAL"
    ) -> investment_models.ExchangeRate:
    """환율 정보 생성"""
    try:
        exchange_rate_data = investment_models.ExchangeRate(
            transaction_id=transaction_id,
            from_currency=currency,
            to_currency="KRW",
            rate=exchange_rate,
            date=date,
            source=source
        )
        db.add(exchange_rate_data)
        db.commit()
        db.refresh(exchange_rate_data)
        return exchange_rate_data
    except Exception as e:
        db.rollback()
        raise e
  




def create_exchange_rate(
        db: Session, 
        exchange_rate: investment_schemas.ExchangeRateCreate
    ) -> investment_models.ExchangeRate:
    """환율 정보 생성"""
    db_exchange_rate = investment_models.ExchangeRate(
        from_currency=exchange_rate.from_currency,
        to_currency=exchange_rate.to_currency,
        rate=exchange_rate.rate,
        date=exchange_rate.date,
        source=exchange_rate.source,
        transaction_id=exchange_rate.transaction_id,
        username=exchange_rate.username
    )
    db.add(db_exchange_rate)
    db.commit()
    db.refresh(db_exchange_rate)
    return db_exchange_rate

def get_exchange_rate(db: Session, exchange_rate_id: int) -> Optional[investment_models.ExchangeRate]:
    """특정 환율 정보 조회"""
    return db.query(investment_models.ExchangeRate).filter(
        investment_models.ExchangeRate.id == exchange_rate_id
    ).first()

def get_exchange_rates(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    from_currency: Optional[str] = None,
    to_currency: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    transaction_id: Optional[int] = None,
    username: Optional[str] = None
) -> List[investment_models.ExchangeRate]:
    """환율 정보 목록 조회"""
    query = db.query(investment_models.ExchangeRate)
    
    # 필터 조건 적용
    if from_currency:
        query = query.filter(investment_models.ExchangeRate.from_currency == from_currency)
    if to_currency:
        query = query.filter(investment_models.ExchangeRate.to_currency == to_currency)
    if start_date:
        query = query.filter(investment_models.ExchangeRate.date >= start_date)
    if end_date:
        query = query.filter(investment_models.ExchangeRate.date <= end_date)
    if transaction_id:
        query = query.filter(investment_models.ExchangeRate.transaction_id == transaction_id)
    if username:
        query = query.filter(investment_models.ExchangeRate.username == username)
    
    # 정렬 및 페이지네이션
    return query.order_by(investment_models.ExchangeRate.date.desc()).offset(skip).limit(limit).all()

def get_exchange_rates_by_transaction(
    db: Session, 
    transaction_id: int
) -> List[investment_models.ExchangeRate]:
    """특정 거래의 환율 정보 목록 조회"""
    return db.query(investment_models.ExchangeRate).filter(
        investment_models.ExchangeRate.transaction_id == transaction_id
    ).all()

def get_latest_exchange_rate(
    db: Session,
    from_currency: str,
    to_currency: str,
    before_date: Optional[datetime] = None,
    username: Optional[str] = None
) -> Optional[investment_models.ExchangeRate]:
    """최신 환율 정보 조회"""
    query = db.query(investment_models.ExchangeRate).filter(
        investment_models.ExchangeRate.from_currency == from_currency,
        investment_models.ExchangeRate.to_currency == to_currency
    )
    
    if before_date:
        query = query.filter(investment_models.ExchangeRate.date <= before_date)
    if username:
        query = query.filter(investment_models.ExchangeRate.username == username)
    
    return query.order_by(investment_models.ExchangeRate.date.desc()).first()

def update_exchange_rate(
    db: Session,
    exchange_rate_id: int,
    exchange_rate_update: investment_schemas.ExchangeRateCreate
) -> Optional[investment_models.ExchangeRate]:
    """환율 정보 수정"""
    db_exchange_rate = get_exchange_rate(db, exchange_rate_id)
    if not db_exchange_rate:
        return None
    
    # 업데이트할 필드들을 딕셔너리로 변환
    update_data = exchange_rate_update.dict(exclude_unset=True)
    
    # 각 필드 업데이트
    for field, value in update_data.items():
        setattr(db_exchange_rate, field, value)
    
    db.commit()
    db.refresh(db_exchange_rate)
    return db_exchange_rate

def delete_exchange_rate(db: Session, exchange_rate_id: int) -> bool:
    """환율 정보 삭제"""
    db_exchange_rate = get_exchange_rate(db, exchange_rate_id)
    if not db_exchange_rate:
        return False
    
    db.delete(db_exchange_rate)
    db.commit()
    return True

def get_exchange_rates_by_date_range(
    db: Session,
    from_currency: str,
    to_currency: str,
    start_date: datetime,
    end_date: datetime,
    username: Optional[str] = None
) -> List[investment_models.ExchangeRate]:
    """특정 기간의 환율 정보 목록 조회"""
    query = db.query(investment_models.ExchangeRate).filter(
        and_(
            investment_models.ExchangeRate.from_currency == from_currency,
            investment_models.ExchangeRate.to_currency == to_currency,
            investment_models.ExchangeRate.date >= start_date,
            investment_models.ExchangeRate.date <= end_date
        )
    )
    
    if username:
        query = query.filter(investment_models.ExchangeRate.username == username)
    
    return query.order_by(investment_models.ExchangeRate.date.asc()).all()

def get_average_exchange_rate(
    db: Session,
    from_currency: str,
    to_currency: str,
    start_date: datetime,
    end_date: datetime,
    username: Optional[str] = None
) -> Optional[float]:
    """특정 기간의 평균 환율 계산"""
    query = db.query(
        func.avg(investment_models.ExchangeRate.rate)
    ).filter(
        and_(
            investment_models.ExchangeRate.from_currency == from_currency,
            investment_models.ExchangeRate.to_currency == to_currency,
            investment_models.ExchangeRate.date >= start_date,
            investment_models.ExchangeRate.date <= end_date
        )
    )
    
    if username:
        query = query.filter(investment_models.ExchangeRate.username == username)
    
    result = query.scalar()
    return float(result) if result is not None else None

def bulk_create_exchange_rates(
    db: Session,
    exchange_rates: List[investment_schemas.ExchangeRateCreate]
) -> List[investment_models.ExchangeRate]:
    """다수의 환율 정보 일괄 생성"""
    db_exchange_rates = [
        investment_models.ExchangeRate(
            from_currency=er.from_currency,
            to_currency=er.to_currency,
            rate=er.rate,
            date=er.date,
            source=er.source,
            transaction_id=er.transaction_id,
            username=er.username
        )
        for er in exchange_rates
    ]
    
    db.add_all(db_exchange_rates)
    db.commit()
    
    for er in db_exchange_rates:
        db.refresh(er)
    
    return db_exchange_rates


