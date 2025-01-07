from fastapi import APIRouter, Depends
from typing import Optional
from datetime import date
import time
from app.utils.dependencies import get_current_user
from app.utils.apt_utils import get_apt_transactions, get_apt_transactions_df_db, get_apt_transactions_year_month, AptDataManager, get_data_year_month
from app.utils.utils import DateUtils
from app.crud.transactions import save_dataframe_to_db, get_unique_dates
from app.crud import transactions as transactions_crud
from app.utils.dependencies import get_db  # 상단에 추가
from sqlalchemy.orm import Session  # 상단에 추가
import pandas as pd
import numpy as np

router = APIRouter()


@router.get("/transactions")
async def get_transactions_apt(
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db),
        property_type: str='아파트',
        trade_type: str='매매',
        sigungu_code: str='51150',
        start_year_month: str=DateUtils.get_5_year_ago_date(DateUtils.get_current_date()),
        end_year_month: str=DateUtils.get_current_date(), 
        dong_name: str=None,
        apt_name: str=None, 
        sort_type: str='desc',  # 'asc' 또는 'desc'
        sort_column: str='dealYear',  # 정렬 기준 컬럼
        pyung_type: str=None,  # 추가: 평수 타입 파라미터
        page: int=1,
        page_size: int=50,
    ):
    """아파트 실거래가 목록 조회
    정렬 가능한 컬럼들:
    - dealYear: 거래년도
    - dealMonth: 거래월
    - dealDay: 거래일
    - dealAmount: 거래금액
    - excluUseAr: 전용면적
    - floor: 층
    - aptNm: 아파트명
    - umdNm: 동이름
    평수 타입:
    - under10: 10평 미만
    - py10: 10평대
    - py20: 20평대
    - py30: 30평대
    - over40: 40평 이상
    """
    print("start_year_month:", start_year_month, "end_year_month:", end_year_month)
    start_time = time.time()
    db_dates = transactions_crud.get_unique_dates(db=db, sigungu_code=sigungu_code)
    # dong_list = transactions_crud.get_dong_list(db=db, sigungu_code=sigungu_code)
    end_time = time.time()
    print(f"DB 조회 시간: {end_time - start_time:.2f}초")
    
    # DB에서 데이터 조회
    db_data = transactions_crud.get_transactions(
        db=db,
        property_type=property_type,
        trade_type=trade_type,
        sigungu_code=sigungu_code,
        start_year_month=start_year_month,
        end_year_month=end_year_month
    )
    
    # API에서 새로운 데이터 가져오기
    df, dates = get_apt_transactions_df_db(
        property_type=property_type,
        trade_type=trade_type,
        sigungu_code=sigungu_code,
        start_year_month=start_year_month,
        end_year_month=end_year_month,
    )
    # DB 데이터와 새로운 데이터 합치기
    if not db_data.empty and not df.empty:
        if '_sa_instance_state' in db_data.columns:
            db_data = db_data.drop('_sa_instance_state', axis=1)
        combined_df = pd.concat([db_data, df], ignore_index=True).drop_duplicates()
    else:
        combined_df = df if not df.empty else db_data
        if '_sa_instance_state' in combined_df.columns:
            combined_df = combined_df.drop('_sa_instance_state', axis=1)

    # NaN 값을 None으로 변환
    combined_df = combined_df.replace({np.nan: None})

    # 평수 필터링
    if pyung_type and not combined_df.empty:
        # m² to 평 변환 (1평 = 3.3058m²)
        combined_df['pyung'] = pd.to_numeric(combined_df['excluUseAr'], errors='coerce') / 3.3058
        
        if pyung_type == 'under10':
            combined_df = combined_df[combined_df['pyung'] < 10]
        elif pyung_type == 'py10':
            combined_df = combined_df[(combined_df['pyung'] >= 10) & (combined_df['pyung'] < 20)]
        elif pyung_type == 'py20':
            combined_df = combined_df[(combined_df['pyung'] >= 20) & (combined_df['pyung'] < 30)]
        elif pyung_type == 'py30':
            combined_df = combined_df[(combined_df['pyung'] >= 30) & (combined_df['pyung'] < 40)]
        elif pyung_type == 'over40':
            combined_df = combined_df[combined_df['pyung'] >= 40]

        # 임시 컬럼 제거
        combined_df = combined_df.drop('pyung', axis=1)

    # 정렬
    if sort_column and not combined_df.empty:
        ascending = True if sort_type == 'asc' else False
        
        if sort_column in ['dealYear', 'dealMonth', 'dealDay']:
            combined_df = combined_df.sort_values(
                by=['dealYear', 'dealMonth', 'dealDay'], 
                ascending=[ascending, ascending, ascending]
            )
        elif sort_column == 'dealAmount':
            # 거래금액 정렬 로직 수정
            try:
                # '만원' 제거하고 숫자로 변환
                combined_df['dealAmount_sort'] = combined_df['dealAmount'].astype(str).str.replace(',', '').str.replace('만원', '').astype(float)
                combined_df = combined_df.sort_values(by='dealAmount_sort', ascending=ascending)
                combined_df = combined_df.drop('dealAmount_sort', axis=1)
            except Exception as e:
                print(f"거래금액 정렬 중 오류 발생: {e}")
                print("dealAmount 컬럼 샘플:", combined_df['dealAmount'].head())
        elif sort_column == 'excluUseAr':
            combined_df['excluUseAr'] = pd.to_numeric(combined_df['excluUseAr'], errors='coerce')
            combined_df = combined_df.sort_values(by='excluUseAr', ascending=ascending)
        else:
            combined_df = combined_df.sort_values(by=sort_column, ascending=ascending)

    # 동 리스트 조회
    dong_list = combined_df['umdNm'].unique().tolist() if not combined_df.empty else []
    dong_list.sort()

    # 동 필터링
    if dong_name and not combined_df.empty:
        combined_df = combined_df[combined_df['umdNm'] == dong_name]

    # 아파트 필터링
    if apt_name and not combined_df.empty:
        combined_df = combined_df[combined_df['aptNm'] == apt_name]

    # 아파트 리스트 조회
    apt_list = combined_df['aptNm'].unique().tolist() if not combined_df.empty else []
    apt_list.sort()

    # 페이지네이션 적용
    if combined_df.empty:
        return {
            "dong_list": [],
            "apt_list": [],
            "data": [],
            "pagination": {
                "total_records": 0,
                "total_pages": 0,
                "current_page": page,
                "page_size": page_size,
                "has_next": False,
                "has_prev": False
            }
        }

    total_records = len(combined_df)
    total_pages = (total_records + page_size - 1) // page_size
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    paginated_df = combined_df.iloc[start_idx:end_idx]
    
    records = paginated_df.to_dict('records')
    records = [{k: (None if isinstance(v, float) and (np.isinf(v) or np.isnan(v)) else v) 
               for k, v in record.items()} 
              for record in records]
    
    return {
        "dong_list": dong_list,
        "apt_list": apt_list,
        "data": records,
        "pagination": {
            "total_records": total_records,
            "total_pages": total_pages,
            "current_page": page,
            "page_size": page_size,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
    
    
@router.get("/dong_list")
async def get_dong_list(
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db),
        sigungu_code: str='51150'
    ):
    """동 리스트 조회"""
    print("sigungu_code:", sigungu_code)
    dong_list = transactions_crud.get_dong_list(db=db, sigungu_code=sigungu_code)
    return {"message": dong_list}
    
    
@router.get("/apt_list")
async def get_apt_list(
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db),
        sigungu_code: str='51150',
        dong_name: str='대흥동'
    ):
    """아파트 리스트 조회"""
    apt_list = transactions_crud.get_apt_list(db=db, sigungu_code=sigungu_code, dong_name=dong_name)
    print("apt_list:", apt_list)
    return {"message": apt_list}

# @router.get("/transactions_year_month")
# async def get_transactions_apt_year_month(
#         property_type: str='아파트',
#         trade_type: str='매매',
#         sigungu_code: str='51150',
#         start_year_month: str='202401',
#         end_year_month: str='202410'
#     ):
#     """아파트 거래 년월 데이터 조회"""
#     # print("start_year_month:", start_year_month, "end_year_month:", end_year_month)
#     year_month_list = get_apt_transactions_year_month(
#         property_type=property_type,
#         trade_type=trade_type,
#         sigungu_code=sigungu_code,
#         start_year_month=start_year_month,
#         end_year_month=end_year_month
#     )
#     print("start_year_month:", start_year_month, "end_year_month:", end_year_month)
#     for i, year_month in enumerate(year_month_list):
#         print(f"{i+1}/{len(year_month_list)} {year_month}")
#         df = get_data_year_month(property_type, trade_type, sigungu_code, year_month)
#         save_dataframe_to_db(df)