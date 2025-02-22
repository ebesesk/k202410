from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date
from app.db.session import get_asset_db
from app.models.investment_models_v3 import AssetTransaction, AssetPrice, Position, Asset
from app.schemas import investment_schemas_v3 as schemas
from app.crud.v3 import assets as crud

router = APIRouter()

@router.post("", response_model=schemas.AssetTransaction)
async def create_asset(
    asset: schemas.AssetTransaction,
    db: Session = Depends(get_asset_db)
):
    """자산 생성"""
    return await crud.create_asset(db=db, asset=asset)

# @router.get("/", response_model=List[schemas.AssetTransactionBase])
# async def get_assets(
#     asset_type: Optional[str] = None,
#     currency: Optional[str] = None,
#     is_active: bool = True,
#     search: Optional[str] = None,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=1000),
#     db: Session = Depends(get_asset_db)
# ):
#     """자산 목록 조회"""
#     return await crud.get_assets(
#         db=db,
#         asset_type=asset_type,
#         currency=currency,
#         is_active=is_active,
#         search=search,
#         skip=skip,
#         limit=limit
#     )

# @router.get("/{asset_id}", response_model=schemas.Asset)
# async def get_asset(
#     asset_id: int,
#     db: Session = Depends(get_asset_db)
# ):
#     """자산 상세 조회"""
#     asset = await crud.get_asset(db=db, asset_id=asset_id)
#     if not asset:
#         raise HTTPException(status_code=404, detail="Asset not found")
#     return asset

# @router.put("/{asset_id}", response_model=schemas.Asset)
# async def update_asset(
#     asset_id: int,
#     asset: schemas.AssetCreate,
#     db: Session = Depends(get_asset_db)
# ):
#     """자산 정보 수정"""
#     updated_asset = await crud.update_asset(db=db, asset_id=asset_id, asset=asset)
#     if not updated_asset:
#         raise HTTPException(status_code=404, detail="Asset not found")
#     return updated_asset

# @router.delete("/{asset_id}", response_model=schemas.Asset)
# async def delete_asset(
#     asset_id: int,
#     db: Session = Depends(get_asset_db)
# ):
#     """자산 삭제"""
#     asset = await crud.delete_asset(db=db, asset_id=asset_id)
#     if not asset:
#         raise HTTPException(status_code=404, detail="Asset not found")
#     return asset