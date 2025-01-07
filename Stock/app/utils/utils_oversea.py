import cryptocode
import getpass
import requests
import json
import os
import websockets
import asyncio
import sys
import redis
# import utils
# from ..core.config import settings
from app.core.config import settings

OPEN_API_KEY = settings.OVERSEA_API_KEY
TOKEN_FILE = settings.OVERSEA_TOKEN_FILE
DOMAIN = settings.DOMAIN
WEBSOCKET_URL = settings.WEBSOCKET_URL

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

def get_access_token(key):
    try:
        print('TOKEN_FILE:', TOKEN_FILE)
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


def get_accno_COSOQ00201(key):
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
    path = "/stock/COSOQ00201"
    url = DOMAIN + path
    headers = {
        "content-type":"application/json; charset=utf-8",
        "authorization":f"Bearer {access_token}",
        "tr_cd":"COSOQ00201",    # 거래 CD
        "tr_cont":"N",      # 연속 거래 여부
        "tr_cont_key":""    # 연속 거래 Key
    }
    body = {
        "t0424InBlock":
        {
            "RecCnt":"00001",
            "AcntNo":"01145701668",
            "Pwd":"535618",
            "BaseDt":"",
            "CrcyCode":"All",
            "AstkBalTpCode":"00"
        }
    }
    
    res = request_api(url, headers, body)
    _accno = json.loads(res.content.decode('utf-8'))
    print('_accno:', _accno)
    # if _accno["rsp_cd"] != "00000":
    #     del_file(TOKEN_FILE)
    #     res = request_api(url, headers, body)

    # _accno_str = res.content.decode('utf-8')

    # for i in elmnt.keys():
    #     _accno_str = _accno_str.replace('"'+i+'"', '"'+elmnt[i]+'"')
    #     # _accno = _accno.replace('"'+i+'"', '"'+elmnt[i]+'"')
    
    # _accno = json.loads(_accno_str)
    
    # _accno_list = [
    #     list(_accno["t0424OutBlock"].keys()), 
    #     list(_accno["t0424OutBlock"].values()), 
    #     list(_accno["t0424OutBlock1"][0].keys())
    # ]
    # for i in _accno["t0424OutBlock1"]:
    #     _accno_list.append(list(i.values()))
    
    # return _accno_list

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
    return json.loads(res.content.decode('utf-8'))
    
def on_message(ws, msg):
    # msg = json.loads(msg.decode('utf-8'))
    msg = json.loads(msg)
    print(msg)
def on_error(ws, msg):
    print(msg)
def on_close(ws):
    print("### closed ###")
def on_open(ws, message):
    ws.send(json.dumps(message))  


# path = "/websocket"
# url = WEBSOCKET_URL + path
# ws = websockets.connect(url, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)


async def connect(key, tr_cd, tr_key, tr_type="3"):
    
    # Redis 연결
    redis_client = redis.Redis(
        host='localhost',  # Redis 호스트
        port=6379,        # Redis 포트
        db=0              # Redis DB 번호
    )
    
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
                    print('res: ', res['body'])
                # 뉴스 채널 설정
                    if res['header']['tr_cd'] == 'NWS':
                        channel = f"stock:nws"
                        redis_client.publish(channel, json.dumps(res))
                        print('ws: ', res['header']['tr_cd'])
                    
                    # 주식 채널 설정
                    else:
                        stock_code = res['body']['tr_key']
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
    
async def main(tasks):
    futures = [connect(t[0], t[1], t[2]) for t in tasks]
    await asyncio.gather(*futures)

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
    loop.run_until_complete(main(tasks))
    
    
    
    
# print(websockets.version.version)
# w = websockets.connect(WEBSOCKET_URL)
# w.send(_str)
# data = w.recv()
# print(data)

