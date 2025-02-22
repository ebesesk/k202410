from fastapi import APIRouter
# from Stock.app.api.v2.investmentLog import security_transactions
from app.api.v1.endpoints import investment
from app.api.v2.investmentLog import (exchange_transactions, 
                                      cash_transactions, 
                                      security_transactions, 
                                      positions, 
                                      income, 
                                      expense,
                                      transactions)

api_router = APIRouter()

# 기존 라우터 유지
api_router.include_router(investment.router, prefix="/investments", tags=["investments"])

# 새로운 라우터들 추가
api_router.include_router(security_transactions.router, prefix="/investments/v2", tags=["security"])
api_router.include_router(exchange_transactions.router, prefix="/investments/v2", tags=["exchange"])
api_router.include_router(cash_transactions.router, prefix="/investments/v2", tags=["cash"])
api_router.include_router(positions.router, prefix="/investments/v2", tags=["positions"])
api_router.include_router(income.router, prefix="/investments/v2", tags=["income"])
api_router.include_router(expense.router, prefix="/investments/v2", tags=["expense"])
api_router.include_router(transactions.router, prefix="/investments/v2", tags=["transactions"])
