import cryptocode
import getpass
import requests
import json
import os
import websockets
import asyncio
import sys
import redis
import signal
import time
# import utils
# from ..core.config import settings
# from app.core.config import settings

# 10분 후 종료를 위한 타이머 설정
TIMEOUT_SECONDS = 600  # 10분

OPEN_API_KEY = 'oqom3khqO3MfMSrhmQ5LEuNF6IOUdhdIFBVR4XC1V89jd6oECofx2uHJeBvQAxnO6CexXTJ9YQhn69xSa6Ry7PQjs4eL*YyhIKuJyz0kgSiIVV4JIrw==*0SBvKyAXu0Pzc9/kWU/quw==*3HCnVoZzZ9vxBbF9OoN11g=='
# APP_SECRET = '0TA2cD/tEsfZcxpy/FBAX2sBJD4yWHVLvidxyp34MIQ=*VywNfGq6e3ZDgwkeCgebAg==*E0aYVBQF1LSucOWYP0PRPw==*M/+lsSnA32LULyHoQjZ70A=='
# API_KEY_FILE = "/home/kds/k202410/Stock/OPENAPI_KEY"
RES_PATH = "/home/kds/k202410/Stock/app/utils/Res"
TOKEN_FILE = '/home/kds/k202410/Stock/ACCESS_TOKEN'
DOMAIN = "https://openapi.ls-sec.co.kr:8080"
WEBSOCKET_URL = "wss://openapi.ls-sec.co.kr:9443"

# key = getpass.getpass("비밀번호")
key = '535618'

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

def request_api(url, headers, body):
    return requests.post(url=url, data=json.dumps(body), headers=headers)
#     return json.loads(res.content.decode('utf-8'))

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

def get_access_token(key):
    try:
        encrypt_str = open_file(TOKEN_FILE)
        _time = get_time(key, _decrypt(encrypt_str, key))    
        print('rsp_cd:', _time['rsp_cd'])
        if _time['rsp_cd'] == 'IGW00121':  
            return issue_access_token(key)
        else:
            return _decrypt(encrypt_str, key)
    except:
        return issue_access_token(key)

def issue_access_token(key):

    # encrypt_str = open_file(API_KEY_FILE)
    # descrypt_str = _decrypt(encrypt_str, key)
    api_key = _decrypt(OPEN_API_KEY, key)
    APP_KEY = api_key.split(' ')[0]
    APP_SECRET = api_key.split(' ')[1]
    # print("api_key:", api_key)
    # print('APP_KEY:', APP_KEY)
    # print('APP_SECRET:', APP_SECRET)
    
    PATH = "/oauth2/token"
    url = DOMAIN + PATH
    values = {
        "appkey":APP_KEY,
        "appsecretkey": APP_SECRET,
        "grant_type": "client_credentials",
        "scope": "oob"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    # print('url', url)
    # print('values', values)
    # print('headers', headers)
    
    res = requests.post(url=url, data=values, headers=headers)
    print("res:", res)
    t = json.loads(res.content.decode("UTF8"))
    encrypt_str = _encrypt(t["access_token"], key)
    write_file(TOKEN_FILE, encrypt_str)
    
    return t["access_token"]


def get_accno_t0424(key):
    elmnt = {
        "sunamt" : "추정순자산",
        "dtsunik" : "실현손익",
        "mamt" : "매입금액",
        "sunamt1" : "추정D2예수금",
        "cts_expcode" : "CTS_종목번호",
        "tappamt" : "평가금액",
        "tdtsunik" : "평가손익",
        "expcode" : "종목번호",
        "jangb" : "잔고구분",
        "janqty" : "잔고수량",
        "mdposqt" : "매도가능수량",
        "pamt" : "평균단가",
        "mamt" : "매입금액",
        "sinamt" : "대출금액",
        "lastdt" : "만기일자",
        "msat" : "당일매수금액",
        "mpms" : "당일매수단가",
        "mdat" : "당일매도금액",
        "mpmd" : "당일매도단가",
        "jsat" : "전일매수금액",
        "jpms" : "전일매수단가",
        "jdat" : "전일매도금액",
        "jpmd" : "전일매도단가",
        "sysprocseq" : "처리순번",
        "loandt" : "대출일자",
        "hname" : "종목명",
        "marketgb" : "시장구분",
        "jonggb" : "종목구분",
        "janrt" : "보유비중",
        "price" : "현재가",
        "appamt" : "평가금액",
        "dtsunik" : "평가손익",
        "sunikrt" : "수익율",
        "fee" : "수수료",
        "tax" : "제세금",
        "sininter" : "신용이자",
    }
    access_token = get_access_token(key)
    path = "/stock/accno"
    url = DOMAIN + path
    headers = {
        "content-type":"application/json; charset=utf-8",
        "authorization":f"Bearer {access_token}",
        "tr_cd":"t0424",
        "tr_cont":"N",
        "tr_cont_key":""
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

    if _accno["rsp_cd"] != "00000":
        del_file(TOKEN_FILE)
        res = request_api(url, headers, body)

    _accno_str = res.content.decode('utf-8')

    for i in elmnt.keys():
        _accno_str = _accno_str.replace('"'+i+'"', '"'+elmnt[i]+'"')
        # _accno = _accno.replace('"'+i+'"', '"'+elmnt[i]+'"')
    
    _accno = json.loads(_accno_str)
    
    _accno_list = [
        list(_accno["t0424OutBlock"].keys()), 
        list(_accno["t0424OutBlock"].values()), 
        list(_accno["t0424OutBlock1"][0].keys())
    ]
    for i in _accno["t0424OutBlock1"]:
        _accno_list.append(list(i.values()))
    
    return _accno_list

# # 계좌정보 가져오기
# _accno_list = get_accno_t0424()
# print(_accno_list)

# access_token = get_access_token('535618')
# print('access_token:', access_token)
# header = {"token": access_token, "tr_type":"3"}
# body = {"tr_cd":"K3_", "tr_key":"200710"}
# _str = json.dumps({"header":header, "body":body})

# try:
#     ws.close()
# except:
#     pass

def get_investinfo_t3320(key, gicode):
    access_token = get_access_token(key)
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
    dict_res = open_res_to_dict('t3320')
    # print(dict_res)
    # print(res.content.decode('utf-8'))
    investinfo = json.loads(res.content.decode('utf-8'))    
    return convert_res_key(investinfo, dict_res)

def convert_res_key(res, dict_res):
    '''
    res 파일 읽어서 dict로 변환
    '''
    # 변환된 결과를 저장할 새로운 딕셔너리
    converted_res = {}
    # 각 블록에 대해 처리
    for block in res:
        converted_res[block] = {}
        # 각 키에 대해 처리
        for key in res[block]:
            if key in dict_res:
                new_key = dict_res[key]
                converted_res[block][new_key] = res[block][key]
    return converted_res

def get_time(key, token):
    path = "/etc/time-search"
    url = DOMAIN + path
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
    res = request_api(url, headers, body)
    # print(res.status_code)
    print(json.loads(res.content.decode('utf-8')))
    time.sleep(0.1)
    return json.loads(res.content.decode('utf-8'))
    
# def on_message(ws, msg):
#     # msg = json.loads(msg.decode('utf-8'))
#     msg = json.loads(msg)
#     print(msg)
# def on_error(ws, msg):
#     print(msg)
# def on_close(ws):
#     print("### closed ###")
# def on_open(ws, message):
#     ws.send(json.dumps(message))  


# path = "/websocket"
# url = WEBSOCKET_URL + path
# ws = websockets.connect(url, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)



async def connect(key, tr_cd, tr_key, tr_type="3"):
    
    # Redis 연결
    redis_client = redis.Redis(
        host='localhost',  # Redis 호스트
        port=6379,        # Redis 포트
        db=0,              # Redis DB 번호
        decode_responses=True
    )
    
    # pid 발행
    channel = f"stock:pid"
    redis_client.publish(channel, f"{os.getpid()}")
    
    # print('pid: ', os.getpid())
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
    # print('send: ', _str)
    async with websockets.connect(url) as websocket:
        await websocket.send(_str)
        i = 1
        while True:
            try:
                k = str(i)
                res_json = await websocket.recv()
                res = json.loads(res_json)
                    
                # print('ws: ', res['header']['tr_cd'])
                
                if res['body'] is not None:
                    # print('res: ', res)
                    # # 응답 데이터를 파일로 저장
                    # filename = f"websocket_response.json"
                    # with open(filename, 'a', encoding='utf-8') as f:
                    #     f.write(json.dumps(res, ensure_ascii=False) + '\n')
                    channel = 'stock'
                    redis_client.publish(channel, json.dumps(res, ensure_ascii=False))
                    # print('redis_publish: ', channel, json.dumps(res, ensure_ascii=False))
                    # # 뉴스 채널 설정
                    # if res['header']['tr_cd'] == 'NWS':
                    #     channel = f"stock:news"
                    #     redis_client.publish(channel, json.dumps(res, ensure_ascii=False))
                    #     # redis_client.publish(channel, res)
                    #     # print('ws: ', channel, json.dumps(res))
                    
                    # # 주식 채널 설정
                    # elif res['header']['tr_cd'] == 'S3_' or res['header']['tr_cd'] == 'K3_':
                    #     stock_code = res['header']['tr_key']
                    #     channel = f"stock:juga:{stock_code}"
                    #     # print('channel: ', channel, json.dumps(res))
                    #     redis_client.publish(channel, json.dumps(res, ensure_ascii=False))
                    # else:
                    #     channel = f"stock:etc"
                    #     redis_client.publish(channel, json.dumps(res, ensure_ascii=False))
                    #     # print('기타 데이터:', res)
            
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
    
# 10분 후 종료를 위한 타이머 설정
# TIMEOUT_SECONDS = 600  # 10분

async def main(shcodes):
    try:
        # 10분 타이머 설정
        end_time = time.time() + TIMEOUT_SECONDS
        
        # 코루틴을 태스크로 변환
        tasks = [asyncio.create_task(connect(t[0], t[1], t[2])) for t in shcodes]
        print('tasks:', tasks)
        
        while time.time() < end_time:
            try:
                # 모든 태스크가 완료될 때까지 대기
                done, pending = await asyncio.wait(
                    tasks,
                    timeout=1,
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # 완료된 태스크 처리
                for task in done:
                    try:
                        await task
                    except Exception as e:
                        print(f"Task error: {e}")
                
            except asyncio.TimeoutError:
                continue
            
        print(f"Websocket connection ended after {TIMEOUT_SECONDS} seconds")
        
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        # 남은 태스크 정리
        for task in tasks:
            if not task.done():
                task.cancel()
        
        # 취소된 태스크 완료 대기
        await asyncio.gather(*tasks, return_exceptions=True)

def signal_handler(signum, frame):
    print("Signal received, closing websocket...")
    sys.exit(0)

if __name__ == "__main__":
    # 환경 변수에서 key 읽기
    key = os.environ.get('STOCK_KEY')
    
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if len(sys.argv) > 1:
        # shcodes = (('535618', 'NWS', 'NWS001'),('535618', 'S3_', '042700'),('535618','K3_', '033100'))
        
        # datas는 이제 key가 없는 형태로 전달되므로, key를 추가하여 사용
        shcodes = [(key, *data) for data in json.loads(sys.argv[1])]
        if 'STOCK_KEY' in os.environ:   # 환경 변수에서 key 삭제
            del os.environ['STOCK_KEY']
        print("Starting websockets with:", shcodes)
        print(f"Will run for {TIMEOUT_SECONDS} seconds")
        
        # 새로운 이벤트 루프 생성 및 설정
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(main(shcodes))
        finally:
            loop.close()
            print("Websocket connection closed")