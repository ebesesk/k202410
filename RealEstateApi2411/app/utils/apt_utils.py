import json, os, sys
import requests
import xml
import numpy as np
import PublicDataReader as TransactionPrice
from functools import lru_cache
import pandas as pd
from app.core.config import settings
from datetime import datetime, timedelta
from app.utils.utils import DateUtils


API_KEY = settings.API_KEY
columns_dict = {
    'sggCd': '법정동시군구코드', 
    'umdCd': '법정동읍면동코드', 
    'landCd': '법정동지번코드', 
    'bonbun': '법정동본번코드', 
    'bubun': '법정동부번코드', 
    'roadNm': '도로명', 
    'roadNmSggCd': '도로명시군구코드', 
    'roadNmCd': '도로명코드', 
    'roadNmSeq': '도로명일련번호코드', 
    'roadNmbCd': '도로명지상지하코드', 
    'roadNmBonbun': '도로명건물본번호코드', 
    'roadNmBubun': '도로명건물부번호코드', 
    'umdNm': '법정동', 
    'aptNm': '단지명', 
    'jibun': '지번', 
    'excluUseAr': '전용면적', 
    'dealYear': '계약년도', 
    'dealMonth': '계약월', 
    'dealDay': '계약일', 
    'dealAmount': '거래금액', 
    'floor': '층', 
    'buildYear': '건축년도', 
    'aptSeq': '단지일련번호', 
    'cdealType': '해제여부', 
    'cdealDay': '해제사유발생일', 
    'dealingGbn': '거래유형', 
    'estateAgentSggNm': '중개사소재지', 
    'rgstDate': '등기일자', 
    'aptDong': '아파트동명', 
    'slerGbn': '매도자', 
    'buyerGbn': '매수자', 
    'landLeaseholdGbn': '토지임대부아파트여부', 
}

api = TransactionPrice.TransactionPrice(service_key=API_KEY)

def process_dataframe(df):
    """데이터프레임 전처리"""
    df = df.rename(columns=columns_dict)
    return df

class AptDataManager:
    """아파트 데이터 관리 클래스"""
    
    def __init__(self):
        self._cache = {}  # 메모리 캐시
        self._cache_timeout = 3600  # 캐시 유효시간 (초)
    
    def _get_cache_key(self, property_type, trade_type, sigungu_code, start_year_month, end_year_month):
        """캐시 키 생성"""
        return f"{property_type}_{trade_type}_{sigungu_code}_{start_year_month}_{end_year_month}"
    
    def get_data(self, property_type, trade_type, sigungu_code, start_year_month, end_year_month):
        """데이터 조회 (캐시 확인 후 없으면 API 호출)"""
        cache_key = self._get_cache_key(property_type, trade_type, sigungu_code, start_year_month, end_year_month)
        
        # 캐시 확인
        if cache_key in self._cache:
            cached_data = self._cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < timedelta(seconds=self._cache_timeout):
                return cached_data['data']
        
        # API 호출 및 캐시 저장
        df = api.get_data(
            property_type=property_type,
            trade_type=trade_type,
            sigungu_code=sigungu_code,
            start_year_month=start_year_month,
            end_year_month=end_year_month
        )
        
        if df is not None and not df.empty:
            # processed_df = process_dataframe(df)
            processed_df = df
            self._cache[cache_key] = {
                'data': processed_df,
                'timestamp': datetime.now()
            }
            return processed_df
        return None
    
    def filter_data(self, df, filters=None, columns=None):
        """데이터 필터링"""
        if df is None:
            return None
            
        try:
            # 필터 적용
            if filters:
                for key, value in filters.items():
                    if key in df.columns:
                        df = df[df[key] == value]
            
            # 특정 컬럼만 선택
            if columns:
                df = df[columns]
            
            return df
            
        except Exception as e:
            print(f"필터링 중 오류 발생: {e}")
            return None


    

# 싱글톤 인스턴스 생성
apt_data_manager = AptDataManager()

def get_data_year_month(property_type, trade_type, sigungu_code, year_month):
    """년월 데이터 조회"""
    df = api.get_data(
        property_type=property_type,
        trade_type=trade_type,
        sigungu_code=sigungu_code,
        year_month=year_month
    )
    return df


def get_apt_transactions(
        property_type: str,
        trade_type: str,
        sigungu_code: str,
        start_year_month: str,
        end_year_month: str,
    ):
    """아파트 거래 정보 조회"""
    try:
        # 캐시된 데이터 조회
        df = apt_data_manager.get_data(
            property_type=property_type,
            trade_type=trade_type,
            sigungu_code=sigungu_code,
            start_year_month=start_year_month,
            end_year_month=end_year_month
        )
        
        if df is None:
            return []
            
        return df.replace({np.nan: None})
        
    except Exception as e:
        print(f"데이터 조회 중 오류 발생: {e}")
        return []


def get_apt_transactions_df_db(
        property_type: str,
        trade_type: str,
        sigungu_code: str,
        start_year_month: str,
        end_year_month: str,
    ):
    """아파트 거래 정보 데이터베이스에서 조회"""
    # 3달 전 ~ 현재 데이터 조회
    month_3ago = DateUtils.get_3_month_ago_date(end_year_month)
    df = apt_data_manager.get_data(property_type, trade_type, sigungu_code, month_3ago, end_year_month)
    
    # start_year_month ~ 4달 전 데이터 조회
    month_4ago = DateUtils.get_1_month_ago_date(month_3ago)
    if start_year_month < month_4ago:   
        dates = DateUtils.to_list(start_year_month, month_4ago)
    elif start_year_month == month_4ago:
        dates = [month_4ago]
    else:
        dates = []

    # print(month_3ago, end_year_month,  start_year_month, month_4ago, dates)
    return df, dates
    # print(df,df_db)
    # return df, df_db

def get_apt_transactions_year_month(
        property_type: str,
        trade_type: str,
        sigungu_code: str,
        start_year_month: str,
        end_year_month: str,
    ):
    """아파트 거래 년월 데이터 조회"""
    month_3ago = DateUtils.get_3_month_ago_date(end_year_month)
    # df = get_apt_transactions(property_type, trade_type, sigungu_code, month_3ago, end_year_month)
    month_4ago = DateUtils.get_1_month_ago_date(month_3ago)
    if start_year_month < month_4ago:   
        year_month_list = DateUtils.to_list(start_year_month, month_4ago)
    elif start_year_month == month_4ago :
        year_month_list = [month_4ago]
    else:
        year_month_list = []
    print(end_year_month, month_3ago, month_4ago, start_year_month, len(year_month_list))
    # print(df,df_db)
    return year_month_list

if __name__ == '__main__':
    get_apt_transactions('아파트', '매매', '11680', '202401', '202411')