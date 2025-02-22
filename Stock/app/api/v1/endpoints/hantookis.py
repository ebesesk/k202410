from fastapi import APIRouter, Depends, Header, Request
from app.utils.dependencies import get_current_user
from sqlalchemy.orm import Session  # 상단에 추가
from app.utils.dependencies import get_db
from app.crud import stock as crud
from app.schemas import stock as schemas
from app.utils import utils


import app.utils.hantuKIS as hantuKIS
import app.utils.fdr_util as fdr_util


router = APIRouter()

@router.get("")
async def get_hantookis():
    return {"message": "한투 KIS API"}

@router.get("/get_access_token")
async def get_kis_access_token(
    db: Session = Depends(get_db),
    key: str = Header(None, alias="X-API-KEY"),
    current_user = Depends(get_current_user)
):
    print('key:', key)
    # print('current_user:', current_user)
    username = current_user['username']
    hantuKIS.get_access_token(db,username,key)
    return {"message": "한투 KIS API"}

@router.get("/get_price_by_code")
async def get_price_by_code(
    request: Request,
    codes: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    ):
    key = request.headers.get('X-API-KEY')
    username = current_user.get('username')
    print('codes:', codes)
    price = fdr_util.get_fdr_price(db, codes)
    print('price:', price)
    # price = hantuKIS.get_price_by_code(db, username, key, code)
    return {"price": price}