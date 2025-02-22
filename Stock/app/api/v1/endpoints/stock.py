from fastapi import APIRouter, Depends, WebSocket, HTTPException, status, BackgroundTasks, Body, Request, Header
from typing import Optional, List
from datetime import date
import time
import redis
from app.utils.dependencies import get_current_user
from sqlalchemy.orm import Session  # 상단에 추가
import pandas as pd
import numpy as np
from app.utils import utils, utils_oversea
from app.utils.test_redis import test_redis_juga_publish as test_redis_juga_publish_utils
import json
from app.crud import stock as crud
from app.schemas import stock as schemas
from app.utils.dependencies import get_db, verify_ws_token
import app.utils.run_websockets as run_websockets
import subprocess, sys, os, signal
import psutil
import base64
from math import ceil
import json
from datetime import timedelta
import pprint
from app.websockets.handlers import handle_websocket, websocket_manager, send_stock_data
import asyncio
from pathlib import Path
from datetime import datetime

router = APIRouter()
# 계좌 정보 호출
ACCNO_LIST = []


@router.get("/")
async def get_stock_info():
    return {"message": "증권 정보 제공 API"}

# Symbol 이 nasdaq, amex, nyse 중 어디에 있는지 확인
@router.get("/check_symbol")
async def check_symbol(
    symbol: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
    ):
    symbol = symbol.upper()
    return utils.check_symbol(db, symbol)

# 시작: 관심종목 불러오기
@router.get("/get_interest_stocks")
async def get_interest_stocks(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
    ):
    '''
    관심종목 불러오기
    '''
    key = request.headers.get('X-API-KEY')
    username = current_user.get('username')
    interest_stock = schemas.InterestStock(username=username)
    _stocks = crud.get_interest_stocks(db, interest_stock)
    if not _stocks:
        raise HTTPException(
            status_code=404,
            detail="관심종목이 없습니다"
        )
    
    shcodes = [stock.종목코드 for stock in _stocks]
    
    # 현재가 조회
    multi_price = utils.get_multi_t8407(key, username, db, ''.join(shcodes))
    # multi_price = multi_price['multi_price_list']   

    
    # 한글기업명 전처리 (특수문자 제거) ##################################################################
    for stock in _stocks:
        stock.한글기업명 = stock.한글기업명.replace('(주)', '').replace(' ', '')
        stock.업종구분명 = stock.업종구분명.replace('FICS ', '').replace(' ', '')
    
    _stocks.sort(key=lambda x: x.업종구분명)    # 업종구분명 정렬
    
    global ACCNO_LIST
    if len(ACCNO_LIST) == 0:
        print('get_interest_stocks: 계좌 데이터 서버에서 받음')
        ACCNO_LIST = utils.get_accno_t0424(key, username, db)
    else:
        print('get_interest_stocks: 계좌 데이터 메모리에서 받음')
        # print('ACCNO_LIST:', ACCNO_LIST)
    accno_codes = [i[0] for i in ACCNO_LIST[3:]]


    result = {
        'shcodes': shcodes,
        '_stocks': _stocks,
        'accno_codes': accno_codes,        
        'multi_price': multi_price,
        'accno_list': ACCNO_LIST,
    }

    return result



# Redis 테스트
@router.get("/test_redis_juga_publish")
async def test_redis_juga_publish(background_tasks: BackgroundTasks):
    '''
    Redis 테스트
    '''
    background_tasks.add_task(test_redis_juga_publish_utils)  # () 제거
    return {"message": "Redis 테스트가 백그라운드에서 시작되었습니다"}




@router.get("/accno")
async def get_accno(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
    ):
    '''
    계좌 정보 호출
    '''
    key = request.headers.get('X-API-KEY')
    username = current_user.get('username')
    global ACCNO_LIST
    accno_list = utils.get_accno_t0424(key, username, db)
    ACCNO_LIST = accno_list
    return {"accno_list": accno_list}



###############DB 관련 API########################
# 관심종목 추가
@router.post("/add_interest_stock")
async def add_interest_stock(
    request: Request,
    # code: str,
    key: str = Body(...),
    code: str = Body(...),
    # stock_input: schemas.InterestStockCodes,
    # key: str = Header(None, alias="X-API-KEY"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
    ):
    # print('stock_input:', stock_input)
    # # key = stock_input.key
    # code = stock_input.code
    stock = schemas.InterestStock(
        username=current_user['username'],
        종목코드=code
    )
    key = request.headers.get('X-API-KEY')
    # print('key:', key)
    # 기존 관심종목 확인
    if crud.get_interest_stock(db, stock):
        raise HTTPException(
            status_code=400,
            detail="이미 등록된 관심종목입니다."
        )
    stock_investinfo = utils.get_investinfo_t3320(key, current_user['username'], db, stock.종목코드)
    stock_juga = utils.get_multi_t8407(key, current_user['username'], db, stock.종목코드)
    print('stock_investinfo:', stock_investinfo)
    print('stock_juga:', stock_juga)
    stock.한글기업명 = stock_investinfo['t3320OutBlock']['한글기업명']
    stock.시장구분 = stock_investinfo['t3320OutBlock']['시장구분']
    stock.업종구분명 = stock_investinfo['t3320OutBlock']['업종구분명']
    print('stock:', stock)
    
    # 투자 정보 조회
    invest_info = {}
    invest_info[stock.종목코드] = {}
    invest_info[stock.종목코드]['t3320OutBlock'] = {}
    invest_info[stock.종목코드]['t3320OutBlock1'] = {}
    invest_info[stock.종목코드]['t8407OutBlock1'] = {}
    invest_info[stock.종목코드]['db'] = {}
    invest_info[stock.종목코드]['t3320OutBlock'] = stock_investinfo['t3320OutBlock']
    invest_info[stock.종목코드]['t3320OutBlock1'] = stock_investinfo['t3320OutBlock1']
    invest_info[stock.종목코드]['t8407OutBlock1'] = stock_juga[0]
    invest_info[stock.종목코드]['db'] = stock.model_dump()
    invest_info[stock.종목코드]['db']['한글기업명'] = stock_investinfo['t3320OutBlock']['한글기업명'].replace('(주)', '').replace(' ', '')
    invest_info[stock.종목코드]['db']['업종구분명'] = stock_investinfo['t3320OutBlock']['업종구분명'].replace(' ', '')
    # 새 관심종목 추가
    print('stock:', stock)
    stock = crud.insert_interest_stock(db, stock)
    return invest_info 
    

# 관심종목 삭제
@router.post("/delete_interest_stocks")
async def delete_interest_stocks(
     request: Request,
    stock_codes: schemas.InterestStockCodes,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
    ):
    '''
    관심종목 삭제
    '''
    key = request.headers.get('X-API-KEY')
    # print('stock_codes:', stock_codes.codes)
    not_found_codes = []
    delete_codes = []
    for code in stock_codes.codes:
        # 사용자별 관심종목 객체 생성
        interest_stock = schemas.InterestStock( 
            username=current_user['username'],
            종목코드=code
        )
        # DB에서 종목 존재 여부 확인
        stock = crud.get_interest_stock(db, interest_stock)
        if not stock:
            not_found_codes.append(code)
            continue
            
        else:
            crud.delete_interest_stock(db, interest_stock)
            delete_codes.append(code)
    if not_found_codes:
        raise HTTPException(
            status_code=404,
            detail=f"다음 종목들을 찾을 수 없습니다: {', '.join(not_found_codes)}"
        )
    print('delete_codes:', delete_codes)
    return {"message": "관심종목 삭제 완료", "delete_codes": delete_codes}

# 관심종목에 tag[memo] 추가
@router.post("/update_interest_stock_tag")
async def update_interest_stock_tag(
    request: Request,
    code: str = Body(...),
    tag: str = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
    ):
    '''
    관심종목에 tag 추가
    '''
    key = request.headers.get('X-API-KEY')
    stock = schemas.InterestStockTag(
            종목코드=code, 
            tag=tag, 
            username=current_user['username']
        )
    load_stock = crud.get_interest_stock(db, stock)
    # 관심종목 존재 확인
    if not load_stock:
        raise HTTPException(
            status_code=404,
            detail="관심종목이 없습니다"
        )
    elif load_stock.tag == tag:
        raise HTTPException(
            status_code=404,
            detail=f"이미 {tag} 태그가 있습니다"
        )
    else:
        return crud.update_interest_stock_tag(db, stock)
    
    
@router.get("/search_stocks")
async def search_stocks(
        query: str,
        request: Request,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
    ):
    """
    종목코드 또는 기업명으로 주식 검색
    """
    key = request.headers.get('X-API-KEY')
    stocks = crud.search_stocks(db, query)
    for stock in stocks:
        print('stock:', stock.shcode, stock.shname, stock.gubun)
   
    return {"stocks": stocks}
    
# 토큰 발급
@router.get("/get_token")
async def get_token(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
    ):
    # print('current_user:', current_user)
    key = request.headers.get('X-API-KEY')
    token = utils.get_access_token(key, current_user['username'], db)
    return {"token": token}

# setup Ls Open API DB저장####################################################
@router.post("/setup_ls_open_api_db")
async def setup_ls_open_api_db(
    request: Request,
    app_key: schemas.AppKey,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
    ):
    '''
    Ls Open API DB 설정
    '''
    key = request.headers.get('X-API-KEY')
    if not (key and app_key.appkey and app_key.appsecretkey):
        raise HTTPException(
            status_code=404,
            detail="key, appkey, appsecretkey가 없습니다"
        )
    encrypt_appkey_str = utils._encrypt(app_key.appkey, key)
    encrypt_appsecretkey_str = utils._encrypt(app_key.appsecretkey, key)
    
    app_key.appkey = encrypt_appkey_str
    app_key.appsecretkey = encrypt_appsecretkey_str
    # print('app_key:', app_key)
    # app_key = schemas.AppKey(
    #     appkey=encrypt_appkey_str,
    #     appsecretkey=encrypt_appsecretkey_str,
    #     cname=app_key.cname,
    #     username=app_key.username,
    # )
    
    crud.insert_app_key(db, app_key)
    return {"message": "Ls Open API DB 설정 완료"}


# # 웹소켓 서버 테스트########################################################################################


# @router.websocket("/ws/{username}/{tr_cd}/{code}")
# async def websocket_endpoint(
#     websocket: WebSocket,
#         username: str,
#         tr_cd: str,
#         code: str
#     ):
#     try:
#         await websocket.accept()  # 여기서 한 번만 accept
#         await handle_websocket(websocket, username, tr_cd, code)
#     except Exception as e:
#         print(f"WebSocket 연결 오류: {str(e)}")
#     finally:
#         try:
#             await websocket.close()
#         except:
#             pass


# @router.get("/test_ws-info")
# async def get_test_websocket_info(
#     # request: Request,
#     tr_cd: str,
#     code: str,
#     key: str = Header(None, alias="X-API-KEY"),
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
#     ):
#     """WebSocket 연결 정보를 반환하는 엔드포인트"""
#     print('get_test_websocket_info:', tr_cd, code, key)
#     try:
#         username = current_user.get('username')
#         ws_url = f"/stock/ws/{username}/{tr_cd}/{code}"
#         return {
#             "status": "success",
#             "websocket_url": ws_url,
#             "username": username,
#             "tr_cd": tr_cd,
#             "code": code
#         }
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": str(e)
#         }
        
        