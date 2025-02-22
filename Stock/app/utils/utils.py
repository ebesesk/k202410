from fastapi import HTTPException
import cryptocode
import getpass
import requests
import json
import os
import websockets
import asyncio
import sys
import redis
import time
# import utils
# from ..core.config import settings
from app.core.config import settings
import redis
from app.schemas import stock as schemas
from app.crud import stock as crud
from sqlalchemy.orm import Session  # 상단에 추가
from fastapi import Depends
from app.utils.dependencies import get_db
from contextlib import contextmanager
from math import ceil
from datetime import datetime, timedelta
import pytz
OPEN_API_KEY = settings.OPEN_API_KEY
TOKEN_FILE = settings.TOKEN_FILE

DOMAIN = settings.DOMAIN
WEBSOCKET_URL = settings.WEBSOCKET_URL
RES_PATH = settings.RES_PATH
# key = getpass.getpass("비밀번호")
# key = '535618'

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_DB = settings.REDIS_DB

CNAME = 'lsopenapi'

@contextmanager
def get_redis_client():
    """Redis 클라이언트 컨텍스트 매니저"""
    client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True
    )
    try:
        yield client
    finally:
        client.close()

def get_current_kst_time():
    kst = pytz.timezone('Asia/Seoul')
    return datetime.now(kst)

def compare_dict(dict_1, dict_2):
    # 키 개수 비교
    if len(dict_1.keys()) != len(dict_2.keys()):
        return False
    # 키 존재 여부 비교
    for key in dict_1:
        if key not in dict_2:
            return False
    # 값 비교
    for key in dict_1:
        if dict_1[key] != dict_2[key]:
            return False
    # 차이점 찾기
    differences = {}
    for key in dict_1:
        if key in dict_2:
            if dict_1[key] != dict_2[key]:
                differences[key] = {
                    'dict_1_value': dict_1[key],
                    'dict_2_value': dict_2[key]
                }
    
    if differences:
        print("차이점 발견:")
        for key, value in differences.items():
            print(f"{key}:")
            print(f"  dict_1: {value['dict_1_value']}")
            print(f"  dict_2: {value['dict_2_value']}")
        return False
    
    return True

def convert_to_kst(dt: datetime):
    kst = pytz.timezone('Asia/Seoul')
    return dt.astimezone(kst) if dt.tzinfo else kst.localize(dt)

# Symbol 이 nasdaq, amex, nyse 중 어디에 있는지 확인
def check_symbol(db: Session, symbol: str):
    if crud.check_symbol_nasdaq(db, symbol):
        return 'nasdaq'
    elif crud.check_symbol_amex(db, symbol):
        return 'amex'
    elif crud.check_symbol_nyse(db, symbol):
        return 'nyse'
    elif crud.get_stock_by_code(db, symbol):
        if crud.get_stock_by_code(db, symbol).gubun == 1:
            return 'kospi'
        else:
            return 'kosdaq'
    else:
        return None

def get_date_str(date):
    return date.strftime("%Y%m%d")

def get_now_date_str():
    return datetime.now().strftime("%Y%m%d")

def _encrypt(_str, key):
    return cryptocode.encrypt(_str, key)

def _decrypt(_str, key):
    return cryptocode.decrypt(_str, key)

def write_file(_file, _str):
    with open(_file, "w") as f:
        f.write(_str)

def open_file(_file):
    with open(_file, "r", encoding='UTF8') as f:
        _txt = f.readline()
    return _txt

# 통신 결과 받기 res.status_code 200 이면 성공
def request_api(url, headers, body):
    res = requests.post(url=url, data=json.dumps(body), headers=headers)
    # print('request_api_res:', res.content.decode("UTF8"))
    if res.status_code != 200:
        raise HTTPException(status_code=400, detail=res.content.decode("UTF8"))
    return res

def del_file(file):
    if os.path.isfile(file):
        os.remove(file)

def open_res_to_dict(tr_code):
    '''
    res 파일 읽어서 dict로 변환
    '''
    _file = RES_PATH + '/' + tr_code + '.res'
    with open(_file, 'r', encoding='euc-kr') as f:
        res = [i.replace('\t', '').replace('\n', '') for i in f.readlines()]
    _d = {}
    for i in range(res.count('begin')):
        _i = [i.split(',') for i in res[res.index('begin')+1:res.index('end')]]
        for j in _i:
            key = j[1].strip()  # 키
            value = j[0].strip() # 값
            _d[key] = value
        res = res[res.index('end')+1:]
    return _d

# 통신 결과 변환 tr_cd == '00000' 이면 성공
def convert_res_key(res, tr_cd):
    '''
    res 파일 읽어서 dict로 변환
    '''
    # print('res:', res)
    dict_res = open_res_to_dict(tr_cd)
    if res['rsp_cd'] != '00000':
        raise HTTPException(status_code=400, detail=res['rsp_msg'])
    
    # 변환된 결과를 저장할 새로운 딕셔너리
    converted_res = {}
    # 각 블록에 대해 처리
    for block in res:
        # 각 키에 대해 처리
        if isinstance(res[block], dict):
            converted_res[block] = {}
            for key in res[block]:
                if key in dict_res:
                    new_key = dict_res[key]
                    converted_res[block][new_key] = res[block][key]
        elif isinstance(res[block], list):
            converted_res[block] = []
            for i in res[block]:
                _dict = {}
                for key in i:
                    if key in dict_res:
                        new_key = dict_res[key]
                        _dict[new_key] = i[key]
                converted_res[block].append(_dict)
        else:
            converted_res[block] = res[block]
    return converted_res

# 토큰 조회
def get_access_token(key, username, db):
    try:
        # Redis에서 토큰 조회
        with get_redis_client() as redis_client:
            encrypt_str = redis_client.get(f"{username}:api_token:{CNAME}")
            # print('encrypt_str:', encrypt_str)
    except:
        print('redis error')
        return issue_access_token(key, username, db)
        
    # 토큰 만료 여부 확인
    try:    
        token = _decrypt(encrypt_str, key)
        # print('_decrypt_token:', token)
    except:
        print('decrypt error')
        return issue_access_token(key, username, db)
    
    # try:
    #     _time = get_time(token)    
    # except Exception as e:
    #     print('get_time:', e)
    #     return issue_access_token(key, username, db)
    _time = get_time(token)
    print('get_time:', _time)
    if _time is False:
        return issue_access_token(key, username, db)
    
    if _time['rsp_cd'] == '00000':
        print('get_access_token: 토큰 유효')
        return token
    elif _time['rsp_cd'] == 'IGW00121':  
        print('get_access_token: api token 만료')
        return issue_access_token(key, username, db)
    else:
        print(detail=_time['rsp_msg'])
        raise HTTPException(status_code=400, detail=_time['rsp_msg'])

# 토큰 발급
def issue_access_token(key: str, username: str, db: Session):

    AppKeyRequest = schemas.AppKeyRequest(
        cname=CNAME,
        username=username,
    )
    
    print('AppKeyRequest:', AppKeyRequest)
    # DB에서 앱키 조회
    app_key = crud.get_app_key(db, AppKeyRequest)
    print('app_key issue_access_token db:', app_key)
    # if not app_key:
    #     raise HTTPException(status_code=400, detail="DB에 앱키가 존재하지 않습니다.")
    try:
        # print('app_key:', app_key.appkey)
        # print('app_key:', app_key.appsecretkey)
        # print('key:', key)
        APP_KEY = _decrypt(app_key.appkey, key)
        APP_SECRET = _decrypt(app_key.appsecretkey, key)    
        # print('APP_KEY success:', APP_KEY)
        # print('APP_SECRET success:', APP_SECRET)
    except:
        # print('APP_KEY:', APP_KEY)
        # print('APP_SECRET:', APP_SECRET)
        raise HTTPException(status_code=400, detail="키가 올바르지 않습니다.")
    
    PATH = "/oauth2/token"
    url = DOMAIN + PATH
    values = {
        "appkey":APP_KEY,
        "appsecretkey": APP_SECRET,
        "grant_type": "client_credentials",
        "scope": "oob"
    }
    # print('APP_KEY:', APP_KEY)
    # print('APP_SECRET:', APP_SECRET)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    res = requests.post(url=url, data=values, headers=headers)
    if res.status_code != 200:
        print('issue_access_token: DB에 앱키가 존재하지 않습니다.')
        raise HTTPException(status_code=400, detail=res.content.decode("UTF8"))
    token = json.loads(res.content.decode("UTF8"))
    
    # 
    write_file(TOKEN_FILE, token["access_token"])
    # Redis 연결 및 토큰 저장
    with get_redis_client() as redis_client:
        encrypt_str = _encrypt(token["access_token"], key)
        redis_client.set(f"{username}:api_token:{CNAME}", encrypt_str)
        redis_client.expire(f"{username}:api_token:{CNAME}", 60*60*24) # 24시간 후 만료
    print('issue_access_token: access_token 재발급')
    return token["access_token"]

# 섹터 조회
def get_sector_t8425(key, username, db):
    access_token = get_access_token(key, username, db)
    path = "/stock/sector"
    url = DOMAIN + path
    headers = {
        "content-type":"application/json; charset=utf-8",
        "authorization":f"Bearer {access_token}",
        "tr_cd":"t8425",
        "tr_cont":"N",
        "tr_cont_key":""
    }
    body = {
        "t8425InBlock":{
            "dummy":"",
        }
    }
    res = request_api(url, headers, body)
    secter = json.loads(res.content.decode('utf-8'))
    return convert_res_key(secter, 't8425')

# 계좌번호 조회
def get_accno_t0424(key, username, db):
    
    access_token = get_access_token(key, username, db)
    # print('get_accno_t0424:', '토큰 발급 완료')
    path = "/stock/accno"
    url = DOMAIN + path
    headers = {
            "content-type":"application/json; charset=utf-8",
            "authorization":f"Bearer {access_token}",
            "tr_cd":"t0424",    # 거래 CD
            "tr_cont":"N",      # 연속 거래 여부
            "tr_cont_key":""    # 연속 거래 Key
        }
    body = {
            "t0424InBlock":
            {
                "prcgb":"1",
                "chegb":"1",
                "dangb":"0",
                "charge":"0",
                "cts_expcode":" "
            }
        }
    
    res = request_api(url, headers, body)
    _accno = json.loads(res.content.decode('utf-8'))
    _accno = convert_res_key(_accno, 't0424')

    
    
    _accno_list = [
        list(_accno["t0424OutBlock"].keys()), 
        list(_accno["t0424OutBlock"].values()), 
        list(_accno["t0424OutBlock1"][0].keys())
    ]
    for i in _accno["t0424OutBlock1"]:
        _accno_list.append(list(i.values()))
    
    return _accno_list

# 투자 정보 조회
def get_investinfo_t3320(key, username, db, gicode):
    access_token = get_access_token(key, username, db)
    path = "/stock/investinfo"
    url = DOMAIN + path
    headers = {
        "content-type":"application/json; charset=utf-8",
        "authorization":f"Bearer {access_token}",
        "tr_cd":"t3320",
        "tr_cont":"N",
        "tr_cont_key":""
    }
    body = {
        "t3320InBlock":{
            "gicode":gicode
        }
    }
    res = request_api(url, headers, body)   
    # dict_res = open_res_to_dict('t3320')
    investinfo = json.loads(res.content.decode('utf-8'))  
    # print('investinfo:', investinfo)
    return convert_res_key(investinfo, "t3320") 

# 기타 데이터 조회
def get_etc_t8436(key, username, db, gubun):
    access_token = get_access_token(key, username, db)
    path = "/stock/etc"
    url = DOMAIN + path
    headers = {
        "content-type":"application/json; charset=utf-8",
        "authorization":f"Bearer {access_token}",
        "tr_cd":"t8436",
        "tr_cont":"N",
        "tr_cont_key":""
    }
    body = {
        "t8436InBlock":{
            "gubun":gubun,
        }
    }
    res = request_api(url, headers, body)
    etc = json.loads(res.content.decode('utf-8'))
    return convert_res_key(etc, 't8430')

# 뉴스 데이터 조회
def get_news_data_t3102(key, username, db, realkey):
    access_token = get_access_token(key, username, db)
    path = "/stock/investinfo"
    url = DOMAIN + path
    headers = {
        "content-type":"application/json; charset=utf-8",
        "authorization":f"Bearer {access_token}",
        "tr_cd":"t3102",
        "tr_cont":"N",
        "tr_cont_key":""
    }
    body = {
        "t3102InBlock":{
            "sNewsno":realkey
        }
    }
    res = request_api(url, headers, body)
    body = json.loads(res.content.decode('utf-8'))
    # 본문 내용 합치기
    content = ''
    for item in body['t3102OutBlock1']:
        content += item['sBody']
        # print('sBody:', item['sBody'])
        
    # 불필요한 문자열 제거 및 정리
    content = content.replace('t3102OutBlock1 ', '')
    content = content.strip()
    return content

def get_time(token):
    path = "/etc/time-search"
    url = DOMAIN + path
    # print('token:', token)
    # print(get_access_token(key))
    # token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6ImE2MDFjYmIwLWY5NDgtNDBlZS05Mjk3LTUxZmFjN2VmZmEyNSIsIm5iZiI6MTczNDk1MjEwMiwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNzM0OTkxMTk5LCJpYXQiOjE3MzQ5NTIxMDIsImp0aSI6IlBTVTloeTdzdTR3Z3ZtY2pkTUhUeUx0SDVyMzZxTVlRZWt1OCJ9.8FzI0hby4nC44_MCTjfUjhmL6xgpdAGw387_gFSQ4-glaZmDhYTJMYPrVa6UBZzKC9zGsdaJ445NiZ6Sm71yQw'
    headers = {
        "content-type":"application/json; charset=utf-8",
        # "authorization":f"Bearer {get_access_token(key)}",
        "authorization":f"Bearer {token}",
        "tr_cd":"t0167",
        "tr_cont":"N",
        "tr_cont_key":""
    }
    body = {
        "t0167InBlock":{
            "id":""
        }
    }
    # print('get_time:', url, headers, body)
    try:    
        res = request_api(url, headers, body)
    except Exception as e:
        print('get_time:', e)
        # raise HTTPException(status_code=400, detail=f'get_time: {str(e)}')
        return False
    # print('res:', json.loads(res.content.decode('utf-8')))
    return json.loads(res.content.decode('utf-8'))
    
def get_multi_t8407(key, username, db, shcodes_str):
    access_token = get_access_token(key, username, db)
    path = "/stock/market-data"
    url = DOMAIN + path
    # nrec를 6으로 나눈 수가 정수가 아닐경우 오류 발생
    nrec = len(shcodes_str)//6
    if len(shcodes_str)%6 != 0:
        raise HTTPException(status_code=400, detail="shcodes의 길이가 6의 배수가 아닙니다.")
    
    headers = {
        "content-type":"application/json; charset=utf-8",
        "authorization":f"Bearer {access_token}",
        "tr_cd":"t8407",
        "tr_cont":"N",
        "tr_cont_key":""
    }
    body = {
        "t8407InBlock":{
            "nrec":nrec,
            # "shcode":shcodes_str
        }
    }
    multi_price = []
    for i in range(ceil(len(shcodes_str)/300)):
        start = i*300
        end = (i+1)*300
        body['t8407InBlock']['shcode'] = shcodes_str[start:end]
        res = request_api(url, headers, body)
        converted_res = convert_res_key(json.loads(res.content.decode('utf-8')), 't8407')
        multi_price.extend(converted_res['t8407OutBlock1'])
        time.sleep(0.5)
    return multi_price

def get_lsopenapi(key, username, db, path, tr_cd, **kwargs):
    print("get_lsopenapi 호출")
    # print('kwargs:', kwargs)
    access_token = get_access_token(key, username, db)
    # print('access_token:', access_token)
    url = DOMAIN + path
    headers = {
        "content-type":"application/json; charset=utf-8",
        "authorization":f"Bearer {access_token}",
        "tr_cd":tr_cd,
        "tr_cont":"N",
        "tr_cont_key":""
    }
    body = {
        f"{tr_cd}InBlock":kwargs
    }
    # print('body:', body)
    # print('headers:', headers)
    res = request_api(url, headers, body)
    res = json.loads(res.content.decode('utf-8'))
    return convert_res_key(res, tr_cd)

# 차트 데이터 조회
day_sdate = None
week_sdate = None
month_sdate = None
def get_chart_data(key, username, db, path, tr_cd, **kwargs):
    
    global day_sdate, week_sdate, month_sdate
    
    period = kwargs['gubun']
    qrycnt = int(kwargs['qrycnt'])
    
    
    # 기본 날짜 설정
    edate = datetime.now().strftime('%Y%m%d')
    sdate = '20150101'  # 기본 시작일

    if period == '2':  # 일봉
        # 일봉 조회 시 최대 100개까지 조회 가능
        # qrycnt = min(500, qrycnt)
        # print('qrycnt:==========', qrycnt)
        qrycnt = int(qrycnt*1.54)
        qrycnt = min(qrycnt, 500)
        sdate = (datetime.now() - timedelta(days=qrycnt)).strftime('%Y%m%d')
        # global day_sdate
        # # day_sdate = sdate
        # print('sdate:==========', sdate)
        
    elif period == '3':  # 주봉
        # 주봉 qrycnt개 를 날짜로 변환
        sdate = (datetime.now() - timedelta(days=qrycnt*7)).strftime('%Y%m%d')
            
    elif period == '4':  # 월봉
        # 월봉 qrycnt개 를 날짜로 변환
        sdate = (datetime.now() - timedelta(days=qrycnt*30)).strftime('%Y%m%d')
        
    elif period == '5':  # 년봉
        # 년봉은 2015년부터
        sdate = '20150101'
        
    # 시작일이 2015년 이전이면 2015년으로 조정
    if sdate < '20150101':
        sdate = '20150101'
        
    # print('sdate:==========', sdate)
    print(f'조회기간: {sdate} ~ {edate}')
    
    # kwargs 업데이트
    kwargs['sdate'] = sdate
    kwargs['edate'] = edate
    kwargs['qrycnt'] = qrycnt
    
    
    kwargs['cts_date'] = " "
    # print('kwargs:', kwargs)
    
    redis_key = f"chart_data:{kwargs['gubun']}:{kwargs['shcode']}"
    # print('redis_key:', redis_key)

    # try:
        # raise Exception('Redis 조회 실패')
        # 캐시 조회
    with get_redis_client() as redis_client:
        cached_data = redis_client.get(redis_key)
        if cached_data:
            print('cached_data 조회 성공:', json.loads(cached_data)[kwargs['shcode']]['chartPeriod'], kwargs['shcode'])
            # print('Redis 조회 성공', json.loads(cached_data)[code]['chartPeriod'])
            # print('cached_data:', len(json.loads(cached_data)[kwargs['shcode']]['data']), kwargs['qrycnt'])
            if day_sdate == sdate and period == '2':
                print('캐시 데이터 사용')
                return json.loads(cached_data)
            elif week_sdate == sdate and period == '3':
                print('캐시 데이터 사용')
                return json.loads(cached_data)
            elif month_sdate == sdate and period == '4':
                print('캐시 데이터 사용')
                return json.loads(cached_data)
        # else:
        #     pass
    # except Exception as e:
    #     print('Redis 조회 실패:', e)
    
    # chart_data = {}
    # API 호출
    # print('OpenAPI 호출')
    # print('kwargs:==========', kwargs)
    time.sleep(1)
    chart_data = get_lsopenapi(key, username, db, path, tr_cd, **kwargs)
    
    try:
        # 캐시 저장
        code = kwargs['shcode']
        chart_data = {code: {'data': chart_data['t8410OutBlock1'], 'chartPeriod':kwargs['gubun']}}
        with get_redis_client() as redis_client:
            # 다음 날 오전 8:50까지 캐시 유지
            next_day = datetime.now().replace(hour=8, minute=50, second=0, microsecond=0)
            if datetime.now() >= next_day:
                next_day += timedelta(days=1)
            ttl = int((next_day - datetime.now()).total_seconds())
            
            redis_client.setex(
                redis_key,
                ttl,
                json.dumps(chart_data)
            )
            if period == '2':
                day_sdate = sdate
            elif period == '3':
                week_sdate = sdate
            elif period == '4':
                month_sdate = sdate
    except Exception as e:
        print('Redis 저장 실패:', e)
        
    print('API 조회 성공', chart_data[code]['chartPeriod'], code)
    
    # print('chart_data===============================================')
    # from pprint import pprint
    # # pprint(chart_data)
    # for i in chart_data[code]['data']:
    #     print(i['날짜'])
    
    return chart_data


async def connect(key, tr_cd, tr_key, tr_type="3"):
    
    
    # # 채널 삭제
    # channels = [f"stock:stock_code", f"stock:pid"]
    # for channel in channels:
    #     if redis_client.exists(channel):
    #         redis_client.delete(channel)
    #         print(f"채널 데이터 삭제 완료: {channel}")
    #     else:
    #         print(f"채널에 데이터가 없습니다: {channel}")
    
    # pid 발행
    channel = f"stock:pid"
    with get_redis_client() as redis_client:
        redis_client.publish(channel, f"{os.getpid()}")
    
    print('pid: ', os.getpid())
    path = "/websocket"
    url = WEBSOCKET_URL + path
    access_token = get_access_token(key)
    header = {
        "token": access_token, 
        "tr_type":tr_type
        }
    body = {
        "tr_cd":tr_cd, 
        "tr_key":tr_key
        }
    _str = json.dumps({"header":header, "body":body})
    
    async with websockets.connect(url) as websocket:
        await websocket.send(_str)
        i = 1
        while True:
            try:
                k = str(i)
                res_json = await websocket.recv()
                res = json.loads(res_json)
                print('ws: ', res['header']['tr_cd'])
                
                if res['body'] is not None:
                    print('res: ', res)
                # 뉴스 채널 설정
                    if res['header']['tr_cd'] == 'NWS':
                        channel = f"stock:nws"
                        with get_redis_client() as redis_client:
                            redis_client.publish(channel, json.dumps(res))
                        print('ws: ', res['header']['tr_cd'])
                    
                    # 주식 채널 설정
                    else:
                        stock_code = res['header']['tr_key']
                        channel = f"stock:stock_code:{stock_code}"
                        redis_client.publish(channel, json.dumps(res))
                
            
            except websockets.exceptions.ConnectionClosedOK as e:
                print('error: ', e)
                break
            
            except KeyboardInterrupt:
                await websocket.close()
                break
            
            if i > 30:
                i = 1
            else:
                i += 1
        
async def main(shcodes):
    futures = [connect(t[0], t[1], t[2]) for t in shcodes]
    print('futures:', futures)
    await asyncio.gather(*futures)

def run(shcodes):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(shcodes))

if __name__ == "__main__":
    # get_access_token('535618')
    # get_ti
    # me('535618')
    # connect('535618', 'NWS', 'NWS001')
    tasks = [
        ('535618', 'NWS', 'NWS001'),
        ('535618', 'S3_', '005930'),
    ]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(tasks))
    
    
    
    