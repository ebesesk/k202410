from fastapi import HTTPException
from sqlalchemy.orm import Session
import cryptocode
import getpass
import requests
import json
import os
import websockets
import asyncio
import sys
import redis
import app.crud.stock as crud
from app.schemas import stock as schemas
# import utils
# from ..core.config import settings
from app.core.config import settings
from app.utils.utils import _encrypt, _decrypt, write_file, open_file, del_file
import mojito

DOMAIN = settings.KIS_DOMAIN
TOKEN_FILE = settings.KIS_TOKEN_FILE
ACCOUNT = settings.KIS_ACCOUNT

def get_access_token(db, username, key):
    print('get_access_token:', key)
    try:
        encrypt_str = open_file(TOKEN_FILE)
        token = _decrypt(encrypt_str, key)
        print('token:', token)
        if token:
            print('토큰 파일 있음')
            return token
        else:
            print('토큰 파일 없음')
            return issue_access_token(db, username, key)
    except Exception as e:
        print('get_access_token:', e)
        return issue_access_token(db, username, key) 

def issue_access_token(db, username,key):
    
    PATH = "/oauth2/tokenP"
    url = DOMAIN + PATH
    
    kis_key = crud.get_app_key(db, schemas.AppKeyRequest(username=username, cname='kis'))
    appkey = _decrypt(kis_key.appkey, key)
    appsecret = _decrypt(kis_key.appsecretkey, key)
    
    body = {
        "grant_type": "client_credentials",
        "appkey": appkey,
        "appsecret": appsecret,
    }
    headers = {"content-type":"application/json"}
    res = requests.post(url=url, data=json.dumps(body), headers=headers)

    if res.status_code == 200:
        token = json.loads(res.content.decode("UTF8"))['access_token']
        write_file(TOKEN_FILE, token)
    else:
        print('res.content:', res.status_code)
        raise HTTPException(status_code=400, detail=res.content.decode("UTF8"))

    print('토큰 발급 완료')
    return token

def get_kis(path: str, tr_id: str, body: dict, db: Session, username: str, key: str):
    
    token = get_access_token(db, username, key)
    url = DOMAIN + path
    
    kis_key = crud.get_app_key(db, schemas.AppKeyRequest(username=username, cname='kis'))
    appkey = _decrypt(kis_key.appkey, key)
    appsecret = _decrypt(kis_key.appsecretkey, key)
    
    headers = {
        "content-Type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": appkey,
        "appsecret": appsecret,
        "personalseckey": "",
        "tr_id": tr_id,
        "tr_cont": json.dumps(body),
        "custtype": "P",
    }
    res = requests.post(url=url, headers=headers, data=json.dumps(body))
    if res.status_code == 200:
        return json.loads(res.content.decode("UTF8"))
    else:
        print('res.content:', res.status_code)
        raise HTTPException(status_code=400, detail=res.content.decode("UTF8"))
