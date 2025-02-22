from fastapi import APIRouter, Depends, Body, Request, Header
import time
import json
from app.utils.dependencies import get_current_user
from sqlalchemy.orm import Session  # 상단에 추가
from app.utils import utils
from app.crud import stock as crud
from app.utils.dependencies import get_db
from app.utils.utils import get_redis_client
from datetime import datetime

router = APIRouter()

# 종목코드로 투자 정보 조회
@router.get("/investinfo_t3320")
async def get_investinfo_t3320(
    request: Request,
    code: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    ):
    key = request.headers.get('X-API-KEY')
    username = current_user.get('username')
    investinfo = utils.get_investinfo_t3320(key, username, db, code)
    return {"investinfo": investinfo}

# 종목코드로 투자 정보 조회 멀티
@router.get("/investinfo_t3320_list")
async def get_investinfo_t3320_list(request: Request,
                                    shcodes: str,
                                    db: Session = Depends(get_db),
                                    current_user = Depends(get_current_user),):
    
    key = request.headers.get('X-API-KEY')
    username = current_user['username']
    def get_seconds_until_midnight():
        now = datetime.now()
        return (24 - now.hour - 1) * 3600 + (60 - now.minute - 1) * 60 + (60 - now.second)

    # Redis 연결 및 토큰 저장
    with get_redis_client() as redis_client:
        investinfo_t3320 = redis_client.get(f"{username}:investinfo_t3320")
        # 메인 로직
        if investinfo_t3320 and investinfo_t3320 != "null":
            print('캐시된 투자정보 사용:', investinfo_t3320)
            investinfo_list = json.loads(investinfo_t3320)
        else:
            print('새로운 투자정보 조회:', investinfo_t3320)
            shcodes = shcodes.split(',')
            investinfo_list = []
            
            # 각 종목코드별 투자정보 조회
            for shcode in shcodes:
                investinfo = utils.get_investinfo_t3320(key, username, db, shcode)
                investinfo_list.append(investinfo)
                time.sleep(1)  # API 호출 간격 조절
            
            # Redis에 저장
            try:
                redis_client.set(
                    f"{username}:investinfo_t3320", 
                    json.dumps(investinfo_list)  # investinfo_list 저장 (기존의 investinfo_t3320이 아님)
                )
                # 자정까지 캐시 유지
                redis_client.expire(
                    f"{username}:investinfo_t3320", 
                    get_seconds_until_midnight()
                )
            except Exception as e:
                print(f"Redis 저장 중 오류 발생: {e}")

        print('최종 투자정보 목록:', investinfo_list)
        return {"investinfo_list": investinfo_list}
    shcodes = shcodes.split(',')
    investinfo_list = []
    username = current_user.get('username')
    for shcode in shcodes:
        investinfo = utils.get_investinfo_t3320(key, username, db, shcode)
        investinfo_list.append(investinfo)
        time.sleep(1)
    
    return {"investinfo_list": investinfo_list}

# 주식종목조회 API용 gubun 0:전체,1:코스피, 2:코스닥
@router.get("/etc_t8436")
async def get_etc_t8436(
    request: Request,
    gubun: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    ):
    key = request.headers.get('X-API-KEY')
    username = current_user.get('username')
    etc = utils.get_etc_t8436(key, username, db, gubun)
    return etc

# API용주식멀티현재가조회 
@router.get("/multi_t8407")
async def get_multi_t8407(
    request: Request,
    shcodes_str: str,
    username: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
    ):
    key = request.headers.get('X-API-KEY')
    if not username:
        username = current_user.get('username')
    multi_price_list = utils.get_multi_t8407(key, username, db, shcodes_str)
    # # print('get_multi_t8407: ', username)
    # for i in range(ceil(len(shcodes_str)/300)):
    #     start = i*300
    #     end = (i+1)*300
    #     multi_price = utils.get_multi_t8407(key, username, db, shcodes_str[start:end])
    #     multi_price_list.extend(multi_price['t8407OutBlock1'])
    
    return {'multi_price_list': multi_price_list}
    
@router.get("/insert_stocks_db")
async def insert_stocks_db(
    request: Request,
    gubun: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    ):
    key = request.headers.get('X-API-KEY')
    username = current_user.get('username')
    stocks = utils.get_etc_t8436(key, username, db, gubun)
    for stock in stocks['t8436OutBlock']:
        print('stock[단축코드]:', stock['단축코드'])
        is_chcode = crud.check_stock_shcode(db, stock['단축코드'])
        if not is_chcode:
            crud.insert_stocks(db, stock)
    return {"message": "종목 추가 완료"}

@router.get("/search_shcode_info")
async def search_shcode_info(
    request: Request,
    shcode: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    ):
    key = request.headers.get('X-API-KEY')
    stock = crud.search_stock_shcode(db, shcode)
    return stock

@router.get("/get_news_data")
async def get_news_data(
    request: Request,
    realkey: str,   
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
    ):
    key = request.headers.get('X-API-KEY')
    username = current_user.get('username')
    news_data = utils.get_news_data_t3102(key, username, db, realkey)
    # print('news_data:', news_data)
    return {"content": news_data}

@router.get("/get_sector")
async def get_sector(
    # request: Request, 
    key: str = Header(None, alias="X-API-KEY"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
    ):
    # key = request.headers.get('X-API-KEY')
    username = current_user.get('username')
    sector = utils.get_sector_t8425(key, username, db)
    return {"sector": sector}
 
@router.post("/get_lsopenapi")
async def get_lsopenapi(
    key: str = Header(None, alias="X-API-KEY"),
    path: str = Body(...),
    tr_cd: str = Body(...),
    kwargs: dict = Body(...),
    # key: str = Header(None, alias="X-API-Key"),  # 헤더 파라미터 추가
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
    ):
    '''
    주식차트 조회
    '''
    username = current_user.get('username')
    result = utils.get_lsopenapi(key, username, db, path, tr_cd, **kwargs)
    # print('result:', result)
    return {"result": result}

@router.post("/get_chart_t8410")
async def get_chart_t8410(
    # request: Request,
    # period: str,    # 2:일봉, 3:주봉, 4:월봉 5:년봉
    key: str = Body(...),
    path: str = Body(...),
    tr_cd: str = Body(...),
    kwargs: dict = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
    ):
    '''
    주식차트 조회
    '''
    # key = request.headers.get('X-API-KEY')
    # print('key:', key)
    # print('path:', path)
    # print('tr_cd:', tr_cd)
    print('kwargs:', kwargs)
    
    
    username = current_user.get('username')
    result = utils.get_chart_data(key, username, db, path, tr_cd, **kwargs)
 
    str_date = utils.get_now_date_str()
    multi_price = utils.get_multi_t8407(key, username, db, kwargs['shcode'])
    # print('multi_price:', multi_price)
    # 최신 데이터 업데이트 오후 15시 30분 이후 ~ 오전 00시
    if kwargs['shcode'] == list(result.keys())[0] and kwargs['gubun'] == '2':
        if multi_price[0]['시가'] != 0:
            result[kwargs['shcode']]['data'][-1]['시가'] = multi_price[0]['시가']
            result[kwargs['shcode']]['data'][-1]['고가'] = multi_price[0]['고가']
            result[kwargs['shcode']]['data'][-1]['저가'] = multi_price[0]['저가']
            result[kwargs['shcode']]['data'][-1]['종가'] = multi_price[0]['현재가']
            result[kwargs['shcode']]['data'][-1]['거래량'] = multi_price[0]['누적거래량']
        else:
            result[kwargs['shcode']]['data'][-1]['종가'] = multi_price[0]['현재가']
    return {"result": result}

@router.post("/get_trade_history")
async def get_trade_history(
    key: str = Header(None, alias="X-API-KEY"),
    path: str = Body(...),
    tr_cd: str = Body(...),
    kwargs: dict = Body(...),
    # key: str = Header(None, alias="X-API-Key"),  # 헤더 파라미터 추가
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
    ):
    '''
    거래내역 조회
    'path':'
    'tr_cd': 'CDPCQ04700'
    kwargs: {
        "RecCnt": 1,            # 0@전체, 1@입출금, 2@입출고, 3@매매, 4@환전, 9@기타
        "QryTp": "0",           # 조회 구분
        "QrySrtDt": "20230515", # 조회 시작일
        "QryEndDt": "20230516", # 조회 종료일
        "SrtNo": 0,            # 조회 시작 번호
        "PdptnCode": "01",      # 상품유형코드 01
        "IsuLgclssCode": "01",  # 종목대분류코드  00@전체, 01@주식, 02@채권, 04@펀드, 03@선물, 05@해외주식, 06@해외파생
        "IsuNo": "KR7000020008" # 종목 번호
    }
    '''
    username = current_user.get('username')
    result = utils.get_lsopenapi(key, username, db, path, tr_cd, **kwargs)
    # print('result:', result)
    return {"result": result}