from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.utils.dependencies import get_investment_db, get_db
from app.utils.dependencies import get_current_user
from app.core.config import settings
from app.utils import dartutil

router = APIRouter()

@router.get("")
def get_dart_list(
    request: Request,
    db: Session = Depends(get_investment_db),
    db_stock: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    key = request.headers.get('X-API-KEY')
    if not key:
        raise HTTPException(status_code=401, detail="X-API-KEY is required")
    
    return {"message": "Hello, World!"}



@router.get("/balance-sheet")
def get_balance_sheet(
    request: Request,
    symbol: str,
    reload: bool = False,
    db: Session = Depends(get_investment_db),
    db_stock: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    key = request.headers.get('X-API-KEY')
    if not key:
        raise HTTPException(status_code=401, detail="X-API-KEY is required")
    # print(current_user['username'])
    
    return dartutil.get_balance_sheet(symbol, current_user['username'], db, db_stock, reload)
    
    
