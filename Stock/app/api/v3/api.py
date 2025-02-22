from fastapi import APIRouter
from app.api.v3.assets import routes as assets
from app.api.v3.assets import prices as asset_prices
from app.api.v3.assets import positions
from app.api.v3.transactions import routes as transactions
from app.api.v3.transactions import cash, trades, income, fees
from app.api.v3.accounts import routes as accounts
from app.api.v3.forex import rates, trades as forex_trades
from app.api.v3.reports import portfolio, pl, transactions as tx_reports
from app.api.v3.accounts import initialize_accounts

api_router = APIRouter()



# Assets
api_router.include_router(assets.router, prefix="/transactions/v3/assets", tags=["transactions_v3"])
api_router.include_router(asset_prices.router, prefix="/transactions/v3/assets/prices", tags=["transactions_v3"])
api_router.include_router(positions.router, prefix="/transactions/v3/positions", tags=["transactions_v3"])

# Transactions
api_router.include_router(transactions.router, prefix="/transactions/v3", tags=["transactions_v3"])
api_router.include_router(cash.router, prefix="/transactions/v3/cash", tags=["transactions_v3"])
api_router.include_router(trades.router, prefix="/transactions/v3/trades", tags=["transactions_v3"])
api_router.include_router(income.router, prefix="/transactions/v3/income", tags=["transactions_v3"])
api_router.include_router(fees.router, prefix="/transactions/v3/fees", tags=["transactions_v3"])

# Accounts
api_router.include_router(accounts.router, prefix="/transactions/v3/accounts", tags=["transactions_v3"])
api_router.include_router(initialize_accounts.router, prefix="/transactions/v3/accounts/initialize", tags=["transactions_v3"])
# Forex
api_router.include_router(rates.router, prefix="/transactions/v3/forex/rates", tags=["transactions_v3"])
api_router.include_router(forex_trades.router, prefix="/transactions/v3/forex/trades", tags=["transactions_v3"])

# Reports
api_router.include_router(portfolio.router, prefix="/transactions/v3/reports/portfolio", tags=["transactions_v3"])
api_router.include_router(pl.router, prefix="/transactions/v3/reports/pl", tags=["transactions_v3"])
api_router.include_router(tx_reports.router, prefix="/transactions/v3/reports/transactions", tags=["transactions_v3"])
