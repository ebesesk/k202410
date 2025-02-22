from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date
from app.db.session import get_asset_db
from app.crud.v3 import reports as crud 
from app.schemas import investment_schemas_v3 as schemas

router = APIRouter()

# @router.get("/summary", response_model=schemas.PortfolioSummary)
# async def get_portfolio_summary(
#     currency: str = "KRW",
#     db: Session = Depends(get_asset_db)
# ):
#     """포트폴리오 요약"""
#     return await crud.get_portfolio_summary(db=db, currency=currency)

# @router.get("/allocation", response_model=List[Dict[str, Any]])
# async def get_portfolio_allocation(
#     group_by: str = Query(..., description="asset_type/currency/sector"),
#     db: Session = Depends(get_asset_db)
# ):
#     """포트폴리오 자산 배분 현황"""
#     return await crud.get_portfolio_allocation(db=db, group_by=group_by)

# @router.get("/performance", response_model=List[Dict[str, Any]])
# async def get_portfolio_performance(
#     start_date: date,
#     end_date: date,
#     interval: str = Query("daily", description="daily/weekly/monthly"),
#     include_dividends: bool = True,
#     db: Session = Depends(get_asset_db)
# ):
#     """포트폴리오 성과 분석"""
#     return await crud.get_portfolio_performance(
#         db=db,
#         start_date=start_date,
#         end_date=end_date,
#         interval=interval,
#         include_dividends=include_dividends
#     )

# @router.get("/risk", response_model=Dict[str, Any])
# async def get_portfolio_risk_metrics(
#     start_date: date,
#     end_date: date,
#     db: Session = Depends(get_asset_db)
# ):
#     """포트폴리오 리스크 메트릭스"""
#     return await crud.get_portfolio_risk_metrics(
#         db=db,
#         start_date=start_date,
#         end_date=end_date
#     )