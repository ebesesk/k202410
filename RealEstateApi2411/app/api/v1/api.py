from fastapi import APIRouter
from app.api.v1.endpoints import bdong_code
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import transactions

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(bdong_code.router, prefix="/bdongcode", tags=["bdongcode"])
api_router.include_router(transactions.router, prefix="/transactionsprice", tags=["transactions_price"])
