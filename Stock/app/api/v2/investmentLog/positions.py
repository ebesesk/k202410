from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.crud.v2 import crud_position_transaction as crud
from app.schemas import investment_schemas_v2


from app.utils.dependencies import get_investment_db
from app.utils.dependencies import get_current_user
from app.core.config import settings
base_accounts = settings.BASE_ACCOUNTS


router = APIRouter(prefix="/positions", tags=["positions"])


@router.get("", response_model=investment_schemas_v2.PositionResponse)
def get_positions(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_investment_db),
    current_user = Depends(get_current_user)
):
    return crud.get_positions(db, current_user["username"], page, limit)

@router.get("/{symbol}", response_model=investment_schemas_v2.PositionResponse)
def get_position_by_symbol(
    symbol: str,
    db: Session = Depends(get_investment_db),
    current_user = Depends(get_current_user)
):
    return crud.get_position_by_symbol(db, symbol, current_user["username"])