from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date
from app.db.session import get_asset_db
from app.schemas import investment_schemas_v3 as schemas
from app.crud.v3 import accounts as crud

router = APIRouter()

@router.post("")
def create_account():
    return {"result": "success"}


# @router.post("/", response_model=schemas.Account)
# async def create_account(
#     account: schemas.AccountCreate,
#     db: Session = Depends(get_asset_db)
# ):
#     """계정 생성"""
#     return await crud.create_account(db=db, account=account)

# @router.get("/", response_model=List[schemas.Account])
# async def get_accounts(
#     account_type: Optional[str] = None,
#     is_active: bool = True,
#     parent_id: Optional[int] = None,
#     search: Optional[str] = None,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=1000),
#     db: Session = Depends(get_asset_db)
# ):
#     """계정 목록 조회"""
#     return await crud.get_accounts(
#         db=db,
#         account_type=account_type,
#         is_active=is_active,
#         parent_id=parent_id,
#         search=search,
#         skip=skip,
#         limit=limit
#     )

# @router.get("/{account_id}", response_model=schemas.Account)
# async def get_account(
#     account_id: int,
#     db: Session = Depends(get_asset_db)
# ):
#     """계정 상세 조회"""
#     account = await crud.get_account(db=db, account_id=account_id)
#     if not account:
#         raise HTTPException(status_code=404, detail="Account not found")
#     return account

# @router.put("/{account_id}", response_model=schemas.Account)
# async def update_account(
#     account_id: int,
#     account: schemas.AccountCreate,
#     db: Session = Depends(get_asset_db)
# ):
#     """계정 정보 수정"""
#     updated_account = await crud.update_account(
#         db=db,
#         account_id=account_id,
#         account=account
#     )
#     if not updated_account:
#         raise HTTPException(status_code=404, detail="Account not found")
#     return updated_account

# @router.delete("/{account_id}", response_model=schemas.Account)
# async def delete_account(
#     account_id: int,
#     db: Session = Depends(get_asset_db)
# ):
#     """계정 삭제"""
#     account = await crud.delete_account(db=db, account_id=account_id)
#     if not account:
#         raise HTTPException(status_code=404, detail="Account not found")
#     return account

# @router.get("/{account_id}/balance", response_model=Dict[str, Any])
# async def get_account_balance(
#     account_id: int,
#     as_of_date: Optional[date] = None,
#     currency: str = "KRW",
#     db: Session = Depends(get_asset_db)
# ):
#     """계정 잔액 조회"""
#     return await crud.get_account_balance(
#         db=db,
#         account_id=account_id,
#         as_of_date=as_of_date,
#         currency=currency
#     )

# @router.get("/{account_id}/transactions", response_model=List[Dict[str, Any]])
# async def get_account_transactions(
#     account_id: int,
#     start_date: Optional[date] = None,
#     end_date: Optional[date] = None,
#     transaction_type: Optional[str] = None,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=1000),
#     db: Session = Depends(get_asset_db)
# ):
#     """계정 거래내역 조회"""
#     return await crud.get_account_transactions(
#         db=db,
#         account_id=account_id,
#         start_date=start_date,
#         end_date=end_date,
#         transaction_type=transaction_type,
#         skip=skip,
#         limit=limit
#     )