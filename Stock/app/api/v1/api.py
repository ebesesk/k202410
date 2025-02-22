from fastapi import APIRouter
from app.api.v1.endpoints import stock
from app.api.v1.endpoints import stock_lsopenapi
from app.api.v1.endpoints import stock_websocket
from app.api.v1.endpoints import trade_log
from app.api.v1.endpoints import hantookis
# from app.api.v1.endpoints import investment
api_router = APIRouter()

api_router.include_router(stock.router, prefix="", tags=["stock"])
api_router.include_router(stock_lsopenapi.router, prefix="", tags=["stock_lsopenapi"])
api_router.include_router(stock_websocket.router, prefix="", tags=["stock_websocket"])
api_router.include_router(trade_log.router, prefix="", tags=["trade_log"])
api_router.include_router(hantookis.router, prefix="/kis", tags=["hantookis"])
# api_router.include_router(investment.router, prefix="/investments", tags=["investments"])