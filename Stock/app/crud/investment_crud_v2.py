from sqlalchemy.orm import Session
from app.models import investment_models
from app.schemas import investment_schemas_v2
from fastapi import HTTPException
from datetime import datetime
from typing import Optional








def create_cash_transaction(
    db: Session, 
    transaction: investment_schemas_v2.CashTransactionCreate,
    username: str
):
    """현금 거래 생성 (입출금, 수익, 비용)"""
    try:
        # 1. 거래 생성
        db_transaction = investment_models.Transaction(
            **transaction.model_dump(),
            username=username
        )
        db.add(db_transaction)
        db.flush()
        
        # 2. 현금 포지션 업데이트
        amount = transaction.amount
        if transaction.type in ["WITHDRAW", "EXPENSE"]:
            amount = -amount
            
        update_position(
            db=db,
            username=username,
            currency=transaction.currency,
            amount=amount
        )
        
        # 3. 포트폴리오 업데이트
        update_portfolio(db=db, username=username)
        
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail='create_cash_transaction error: ' + str(e))











def create_exchange_transaction(
    db: Session, 
    transaction: investment_schemas_v2.ExchangeTransactionCreate,
    username: str
):
    """환전 거래 생성"""
    try:
        # 1. 거래 생성
        db_transaction = investment_models.Transaction(
            **transaction.model_dump(),
            username=username
        )
        db.add(db_transaction)
        db.flush()

        # 2. 환율 정보 저장
        exchange_rate = investment_models.ExchangeRate(
            transaction_id=db_transaction.id,
            from_currency=transaction.currency,
            to_currency=transaction.transaction_metadata["to_currency"],
            rate=transaction.exchange_rate,
            date=transaction.date,
            username=username
        )
        db.add(exchange_rate)
        
        # 3. 포지션 업데이트
        # 출금 통화 감소
        update_position(
            db=db,
            username=username,
            currency=transaction.currency,
            amount=-transaction.amount
        )
        
        # 입금 통화 증가
        to_amount = transaction.amount * transaction.exchange_rate
        update_position(
            db=db,
            username=username,
            currency=transaction.transaction_metadata["to_currency"],
            amount=to_amount
        )
        
        # 4. 포트폴리오 업데이트
        update_portfolio(db=db, username=username)
        
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail='create_exchange_transaction error: ' + str(e))














def create_security_transaction(
    db: Session, 
    transaction: investment_schemas_v2.SecurityTransactionCreate,
    username: str
):
    """증권 거래 생성 (주식, ETF, 암호화폐)"""
    try:
        # 1. 거래 생성
        db_transaction = investment_models.Transaction(
            **transaction.model_dump(),
            username=username
        )
        db.add(db_transaction)
        db.flush()
        
        # 2. 증권 포지션 업데이트
        quantity = transaction.quantity
        if transaction.type in ["STOCK_SELL", "CRYPTO_SELL"]:
            quantity = -quantity
            
        update_position(
            db=db,
            username=username,
            asset_id=transaction.asset_id,
            currency=transaction.currency,
            quantity=quantity
        )
        
        # 3. 현금 포지션 업데이트 (거래대금)
        amount = -(transaction.quantity * transaction.price)
        if transaction.type in ["STOCK_SELL", "CRYPTO_SELL"]:
            amount = -amount
            
        update_position(
            db=db,
            username=username,
            currency=transaction.currency,
            amount=amount
        )
        
        # 4. 포트폴리오 업데이트
        update_portfolio(db=db, username=username)
        
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))








def update_position(
    db: Session,
    username: str,
    asset_id: Optional[int] = None,
    currency: str = None,
    quantity: float = 0,
    amount: float = 0
):
    """포지션 업데이트 (증권 또는 현금)"""
    try:
        if asset_id:  # 증권 포지션
            position = db.query(investment_models.Position).filter(
                investment_models.Position.username == username,
                investment_models.Position.asset_id == asset_id
            ).first()
            
            if not position:
                position = investment_models.Position(
                    username=username,
                    asset_id=asset_id,
                    quantity=0,
                    currency=currency
                )
                db.add(position)
            
            position.quantity += quantity
            position.last_updated = datetime.now()
            
        else:  # 현금 포지션
            position = db.query(investment_models.Position).filter(
                investment_models.Position.username == username,
                investment_models.Position.currency == currency,
                investment_models.Position.asset_id.is_(None)
            ).first()
            
            if not position:
                position = investment_models.Position(
                    username=username,
                    currency=currency,
                    quantity=0
                )
                db.add(position)
            
            position.quantity += amount
            position.last_updated = datetime.now()
            
        db.flush()
        return position
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"포지션 업데이트 실패: {str(e)}")








def update_portfolio(db: Session, username: str):
    """포트폴리오 가치 업데이트"""
    try:
        # 모든 포지션 조회
        positions = db.query(investment_models.Position).filter(
            investment_models.Position.username == username
        ).all()
        
        total_value = 0
        cash_value = 0
        invested_value = 0
        portfolio_metadata = {"positions": {}}
        
        for position in positions:
            if position.asset_id:  # 증권 포지션
                position_value = position.quantity * (position.current_price or 0)
                total_value += position_value
                invested_value += position_value
                portfolio_metadata["positions"][position.asset_id] = {
                    "quantity": position.quantity,
                    "value": position_value,
                    "currency": position.currency
                }
            else:  # 현금 포지션
                cash_value += position.quantity
                total_value += position.quantity
                portfolio_metadata["positions"][position.currency] = {
                    "amount": position.quantity
                }
        
        # 포트폴리오 저장
        portfolio = investment_models.Portfolio(
            username=username,
            date=datetime.now(),
            total_value=total_value,
            cash_value=cash_value,
            invested_value=invested_value,
            portfolio_metadata=portfolio_metadata
        )
        db.add(portfolio)
        db.flush()
        return portfolio
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"포트폴리오 업데이트 실패: {str(e)}")



















