import pandas as pd
import numpy as np
from fastapi import Depends
from sqlalchemy.orm import Session
from app.utils.dependencies import get_db
from sqlalchemy import create_engine
from app.core.config import settings
from app.models.transactions import ApartmentTransactionDB
from app.utils.utils import DateUtils

def save_dataframe_to_db(df, table_name='apt_transactions', if_exists='append'):
    """데이터프레임을 DB에 저장"""
    try:
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
        
        # NaN 값을 None으로 변환
        df = df.replace({np.nan: None})
        
        # 컬럼명 매핑 및 필요한 컬럼만 선택
        required_columns = [
            'sggCd', 'umdCd', 'landCd', 'bonbun', 'bubun', 'roadNm',
            'roadNmSggCd', 'roadNmCd', 'roadNmSeq', 'roadNmBonbun', 'roadNmBubun',
            'umdNm', 'aptNm', 'jibun', 'excluUseAr', 'dealYear', 'dealMonth',
            'dealDay', 'dealAmount', 'floor', 'buildYear', 'aptSeq', 'cdealType',
            'cdealDay', 'dealingGbn', 'estateAgentSggNm', 'rgstDate', 'aptDong',
            'slerGbn', 'buyerGbn', 'landLeaseholdGbn'
        ]
        
        # 데이터프레임의 컬럼명을 DB 스키마에 맞게 변경
        df_columns = df.columns.tolist()
        column_mapping = {}
        for col in df_columns:
            if col in required_columns:
                column_mapping[col] = col
        
        # 필요한 컬럼만 선택하고 이름 변경
        df = df[list(column_mapping.keys())].rename(columns=column_mapping)
        
        # DB에 저장
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists=if_exists,
            index=False,  # id 컬럼은 DB에서 자동 생성되도록 설정
            chunksize=1000
        )
        return True
    except Exception as e:
        print(f"DB 저장 중 오류 발생: {e}")
        return False

def get_unique_dates(db: Session, sigungu_code: str):
    """
    거래 연월 리스트 조회 (중복 제거)
    반환 형식: ['202311', '202310', ...]
    """
    # 쿼리 결과 확인
    db_dates = db.query(ApartmentTransactionDB.dealYear, ApartmentTransactionDB.dealMonth)\
        .distinct()\
        .filter(ApartmentTransactionDB.sggCd == sigungu_code)\
        .order_by(ApartmentTransactionDB.dealYear.desc(), ApartmentTransactionDB.dealMonth.desc())
        
    db_dates = db_dates.all()
    date_list = [f"{row.dealYear}{str(row.dealMonth).zfill(2)}" for row in db_dates]
    date_list.sort()
    return date_list

def get_transactions(db: Session, property_type: str, trade_type: str, 
                    sigungu_code: str, start_year_month: str, end_year_month: str):
    """DB에서 거래 데이터 조회"""
    # start_year_month와 end_year_month에서 년도와 월 추출
    start_year_month = DateUtils.get_3_month_ago_date(start_year_month)
    start_year_month = DateUtils.get_1_month_ago_date(start_year_month)
    start_year = start_year_month[:4]
    start_month = start_year_month[4:]
    end_year = end_year_month[:4]
    end_month = end_year_month[4:]
    
    # query = db.query(ApartmentTransactionDB).filter(
    #     ApartmentTransactionDB.property_type == property_type,
    #     ApartmentTransactionDB.trade_type == trade_type,
    #     ApartmentTransactionDB.sigungu_code == sigungu_code
    # )
    query = db.query(ApartmentTransactionDB).filter(
        ApartmentTransactionDB.sggCd == sigungu_code  # sigunguCode -> sggCd
    )
    # 날짜 조건 추가
    query = query.filter(
        ((ApartmentTransactionDB.dealYear > start_year) | 
         ((ApartmentTransactionDB.dealYear == start_year) & 
          (ApartmentTransactionDB.dealMonth >= int(start_month)))) &
        ((ApartmentTransactionDB.dealYear < end_year) |
         ((ApartmentTransactionDB.dealYear == end_year) & 
          (ApartmentTransactionDB.dealMonth <= int(end_month))))
    )
    
    results = query.all()
    return pd.DataFrame([item.__dict__ for item in results])


def get_dong_list(db: Session, sigungu_code: str):
    """동 리스트 조회"""
    query = db.query(ApartmentTransactionDB.umdNm)\
        .distinct()\
        .filter(ApartmentTransactionDB.sggCd == sigungu_code)\
        .order_by(ApartmentTransactionDB.umdNm)
    
    # 쿼리 결과를 리스트로 변환
    dong_list = [row[0] for row in query.all() if row[0]]  # None 값 제외
    return dong_list

def get_apt_list(db: Session, sigungu_code: str, dong_name: str):
    """아파트 리스트 조회"""
    query = db.query(ApartmentTransactionDB.aptNm)\
        .distinct()\
        .filter(ApartmentTransactionDB.sggCd == sigungu_code)\
        .order_by(ApartmentTransactionDB.aptNm)
    
    # 쿼리 결과를 리스트로 변환하고 None 값 제외
    apt_list = [row[0] for row in query.all() if row[0]]
    return apt_list