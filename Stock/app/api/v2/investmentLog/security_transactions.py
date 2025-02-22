from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.v2 import crud_security_transaction as crud
from app.schemas import investment_schemas_v2


from app.utils.dependencies import get_investment_db, get_db
from app.utils.dependencies import get_current_user
from app.core.config import settings
from app.crud.trade import get_all_trade_log
from app.crud.v2 import crud_transactions as crud_transactions

from pprint import pprint

base_accounts = settings.BASE_ACCOUNTS




router = APIRouter(prefix="/security")




@router.post("")
def create_security_transaction(
    transaction: investment_schemas_v2.SecurityTransactionCreate,
    db: Session = Depends(get_investment_db),
    current_user = Depends(get_current_user),
):

    crud.create_security_transaction_v2(
        db=db,
        transaction=transaction,
        username=current_user["username"],
    )
    return {"message": "거래 기록 완료"}



@router.post("/get-info")
def get_info(
    transaction: investment_schemas_v2.SecurityTransactionCreate,
    db: Session = Depends(get_investment_db),
    current_user = Depends(get_current_user),
):
    return crud.calculate_fifo_sell(
        db=db,
        transaction=transaction,
        username=current_user["username"],
        get_info=True
    )



# @router.get("/fifo-sell-info", response_model=investment_schemas_v2.EstimatePLResponse)
@router.get("/fifo-sell-info")
def get_fifo_sell_info(
    asset_id: int,
    quantity: float,
    price: float,
    db: Session = Depends(get_investment_db),
    current_user = Depends(get_current_user)
):
    """FIFO 매도 정보 조회"""
    username = current_user["username"]
    
    return crud.calculate_fifo_sell_info(db, username, asset_id, quantity, price)


@router.post("/estimate-pl", response_model=investment_schemas_v2.EstimatePLResponse)
def estimate_profit_loss(
    request: investment_schemas_v2.EstimatePLRequest,
    db: Session = Depends(get_investment_db),
    current_user = Depends(get_current_user)
):
    """매도 시 예상 실현손익 계산"""
    username = current_user["username"]
    try:
        # 과거 매수 거래 조회
        buy_transactions = crud.get_historical_buys(
            db=db,
            username=username,
            asset_id=request.asset_id
        )
        
        # FIFO 방식으로 실현손익 계산
        pl_info = crud.calculate_fifo_profit_loss(
            buy_transactions=buy_transactions,
            sell_quantity=request.quantity,
            sell_price=request.price,
            sell_currency=request.currency,
            exchange_rate=request.exchange_rate
        )
        print(
            {"realized_profit_loss": pl_info["realized_profit_loss"],
            "realized_details": pl_info["realized_details"]}
        )
        return {
            "realized_profit_loss": pl_info["realized_profit_loss"],
            "realized_details": pl_info["realized_details"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# @router.get("/get-old-trade-log")
# def get_old_trade_log(
#     db: Session = Depends(get_investment_db),
#     db_stock: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
    
#     crud_transactions.get_old_trade_log(db, db_stock, current_user["username"])
    
            
        


