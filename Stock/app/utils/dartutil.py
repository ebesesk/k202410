import numpy as np
import pandas as pd
import time
from pprint import pprint
from datetime import datetime
import redis
from contextlib import contextmanager
from io import StringIO

import OpenDartReader
from app.crud.stock import get_interest_stock_by_username, get_stock_by_code
from app.core.config import settings


api_key = '24c24e732043f024a09a8ca99d75bcea19837bdf'

dart = OpenDartReader(api_key)

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

# def get_balance_sheets(username, investment_db, stock_db ):
#     interest_stock = get_interest_stock_by_username(stock_db, username)
#     stock_codes = [(stock.종목코드, stock.한글기업명) for stock in interest_stock]
#     # print(stock_codes)
#     ind_list = ["자산총계", "부채총계", "자본총계", "당기순이익", "영업이익"]
#     for stock in stock_codes:
#         report = find_fins_ind_list(stock[0], stock[1], 2023, ind_list)
#         print(report)


def get_balance_sheet(symbol, username, investment_db, stock_db, reload=False):
    '''
    유동자산, 비유동자산, 자산총계, 
    유동부채, 비유동부채, 부채총계, 
    자본금, 이익잉여금, 자본총계, 
    매출액, 영업이익, 법인세차감전 순이익, 당기순이익, 당기순이익(손실), 
    총포괄손익, 
    
    '''    
    ind_list = ["자산총계", "유동자산", "부채총계", "유동부채", "자본총계", "매출액", "당기순이익"]
    stock = get_stock_by_code(stock_db, symbol)
    
    print('symbol:', symbol)
    current_year = datetime.now().year
    _years = [current_year - i for i in range(5)]
    _years.reverse()
    # print('_years:', _years)
    
    
    if symbol == '':
        # for 
        # n개 symbol
        stocks = get_interest_stock_by_username(stock_db, username)
        symbols = [stock.종목코드 for stock in stocks]
        print('개수:', len(symbols))
        n = 3
        symbols_n = []
        for i in range(len(symbols)//n+1):
            print(i)
            symbols_n.append(symbols[i*n:(i+1)*n])
        print(symbols_n)
    
    
    
    # report_year = find_fins_ind_list(stock.shcode, stock.shname, current_year, ind_list)
    # report_year = get_balance_sheet_year(symbol)
    report_quarter = get_balance_sheet_quarter(symbol, reload)
    
    return {
        'quarter': report_quarter,
        # 'report_year': report_year
    }


def get_balance_sheet_year(symbol):
    
    column_name = {'rcept_no': '접수번호',
                    'corp_code': '고유번호',
                    'stock_code': '종목코드',
                    'bsns_year': '사업연도',
                    'reprt_code': '보고서코드',
                    'account_nm': '계정명',     # (예: 자본총계)',
                    'fs_div': '개별연결구분',   # (CFS=연결재무제표, OFS=재무제표)'
                    'fs_nm': '개별연결명',      # (연결재무제표 또는 재무제표)'
                    'sj_div': '재무제표구분',   # (BS=재무상태표, IS=손익계산서)'
                    'sj_nm': '재무제표명',      # (재무상태표 또는 손익계산서)'
                    'thstrm_nm': '당기명',
                    'thstrm_dt': '당기일자',
                    'thstrm_amount': '당기금액',
                    'thstrm_add_amount': '당기누적금액',
                    'frmtrm_nm': '전기명',
                    'frmtrm_dt': '전기일자',
                    'frmtrm_amount': '전기금액',
                    'frmtrm_add_amount': '전기누적금액',
                    'bfefrmtrm_nm': '전전기명',
                    'bfefrmtrm_dt': '전전일자',
                    'bfefrmtrm_amount': '전전기금액',
                    'ord': '계정과목정렬순서',}
    
    year = datetime.now().year - 1
    
    
    reports = {}
    
    report = dart.finstate(corp=symbol, bsns_year=year, reprt_code='11011')
    report = report.rename(columns=column_name)
    reports[year] = report
    report_is = report.copy()
    report_2 = None
    
    is_empty = is_empty_report(report_is)
    print('is_empty:', is_empty)
    if is_empty:
        reports = {}
        report = dart.finstate(corp=symbol, bsns_year=year-1, reprt_code='11011')
        report = report.rename(columns=column_name)
        reports[year-1] = report
        report_2 = dart.finstate(corp=symbol, bsns_year=year-4, reprt_code='11011')
        report_2 = report_2.rename(columns=column_name)
        reports[year-4] = report_2
    else:
        report_2 = dart.finstate(corp=symbol, bsns_year=year-3, reprt_code='11011')
        report_2 = report_2.rename(columns=column_name)
        reports[year-3] = report_2
    
    
    
    pprint(reports)
    reports_index = None
    reports_data = None
    for year, report in reports.items():
        print(year)
        pprint(report)
        report_index = report[['계정명', '당기금액', '전기금액']]
    
    
    
       
       
   
   
   
   
   

def get_balance_sheet_quarter(symbol, reload=False):
    
    reports = None
    with get_redis_client() as redis_client:
        if redis_client.exists(f'{symbol}_balance_sheet') and not reload:
            reports = redis_client.get(f'{symbol}_balance_sheet')
            # StringIO 객체로 감싸서 JSON 읽기
            reports = pd.read_json(StringIO(reports))
        else:
            reports = None
    
    column_name = {'rcept_no': '접수번호',
                    'corp_code': '고유번호',
                    'stock_code': '종목코드',
                    'bsns_year': '사업연도',
                    'reprt_code': '보고서코드',
                    'account_nm': '계정명',     # (예: 자본총계)',
                    'fs_div': '개별연결구분',   # (CFS=연결재무제표, OFS=재무제표)'
                    'fs_nm': '개별연결명',      # (연결재무제표 또는 재무제표)'
                    'sj_div': '재무제표구분',   # (BS=재무상태표, IS=손익계산서)'
                    'sj_nm': '재무제표명',      # (재무상태표 또는 손익계산서)'
                    'thstrm_nm': '당기명',
                    'thstrm_dt': '당기일자',
                    'thstrm_amount': '당기금액',
                    'thstrm_add_amount': '당기누적금액',
                    'frmtrm_nm': '전기명',
                    'frmtrm_dt': '전기일자',
                    'frmtrm_amount': '전기금액',
                    'frmtrm_add_amount': '전기누적금액',
                    'bfefrmtrm_nm': '전전기명',
                    'bfefrmtrm_dt': '전전일자',
                    'bfefrmtrm_amount': '전전기금액',
                    'ord': '계정과목정렬순서',}
    
    
    quarters = ['11013', '11012', '11014', '11011'] # 1분기, 2분기, 3분기, 4분기
    _months = [3, 6, 9, 12]
    
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_quarter = (current_month-1)//3
    
    
    # quarter = 0
    # # year = 0 
    
    # end_quatrer = ''
    
    def get_year_quarter(current_quarter):
        current_year = datetime.now().year
        quarters = ['11013', '11012', '11014', '11011'] # 1분기, 2분기, 3분기, 4분기
        if current_quarter == 0:
            end_quatrer = 3
            end_year = current_year - 1
            start_year = current_year - 2
            start_quarter = 0
            year_quarter = [(start_year-5, quarters[start_quarter]), 
                            (start_year-5, quarters[start_quarter+1]), 
                            (start_year-5, quarters[start_quarter+2]), 
                            (start_year-5, quarters[start_quarter+3]),
                            (start_year-4, quarters[start_quarter]), 
                            (start_year-4, quarters[start_quarter+1]), 
                            (start_year-4, quarters[start_quarter+2]), 
                            (start_year-4, quarters[start_quarter+3]),
                            (start_year-3, quarters[start_quarter]), 
                            (start_year-3, quarters[start_quarter+1]), 
                            (start_year-3, quarters[start_quarter+2]), 
                            (start_year-3, quarters[start_quarter+3]),
                            (start_year-2, quarters[start_quarter]), 
                            (start_year-2, quarters[start_quarter+1]), 
                            (start_year-2, quarters[start_quarter+2]), 
                            (start_year-2, quarters[start_quarter+3]),
                            (start_year-1, quarters[start_quarter]), 
                            (start_year-1, quarters[start_quarter+1]), 
                            (start_year-1, quarters[start_quarter+2]), 
                            (start_year-1, quarters[start_quarter+3]),
                            (start_year, quarters[start_quarter]), 
                            (start_year, quarters[start_quarter+1]), 
                            (start_year, quarters[start_quarter+2]), 
                            (start_year, quarters[start_quarter+3]), 
                            (end_year, quarters[end_quatrer-3]),
                            (end_year, quarters[end_quatrer-2]),
                            (end_year, quarters[end_quatrer-1]),
                            (end_year, quarters[end_quatrer])]
        elif current_quarter == 1:
            end_quatrer = 0
            end_year = current_year
            start_year = current_year - 1
            start_quarter = 0
            year_quarter = [(start_year-5, quarters[start_quarter]), 
                            (start_year-5, quarters[start_quarter+1]), 
                            (start_year-5, quarters[start_quarter+2]), 
                            (start_year-5, quarters[start_quarter+3]),
                            (start_year-4, quarters[start_quarter]), 
                            (start_year-4, quarters[start_quarter+1]), 
                            (start_year-4, quarters[start_quarter+2]), 
                            (start_year-4, quarters[start_quarter+3]),
                            (start_year-3, quarters[start_quarter]), 
                            (start_year-3, quarters[start_quarter+1]), 
                            (start_year-3, quarters[start_quarter+2]), 
                            (start_year-3, quarters[start_quarter+3]),
                            (start_year-2, quarters[start_quarter]), 
                            (start_year-2, quarters[start_quarter+1]), 
                            (start_year-2, quarters[start_quarter+2]), 
                            (start_year-2, quarters[start_quarter+3]),
                            (start_year-1, quarters[start_quarter]), 
                            (start_year-1, quarters[start_quarter+1]), 
                            (start_year-1, quarters[start_quarter+2]), 
                            (start_year-1, quarters[start_quarter+3]),
                            (start_year, quarters[start_quarter]), 
                            (start_year, quarters[start_quarter+1]), 
                            (start_year, quarters[start_quarter+2]), 
                            (start_year, quarters[start_quarter+3]), 
                            (end_year, quarters[end_quatrer-2]),
                            (end_year, quarters[end_quatrer-1]),
                            (end_year, quarters[end_quatrer])]
        elif current_quarter == 2:
            end_quatrer = 1
            end_year = current_year
            start_year = current_year - 1
            start_quarter = 0
            year_quarter = [(start_year-5, quarters[start_quarter]), 
                            (start_year-5, quarters[start_quarter+1]), 
                            (start_year-5, quarters[start_quarter+2]), 
                            (start_year-5, quarters[start_quarter+3]),
                            (start_year-4, quarters[start_quarter]), 
                            (start_year-4, quarters[start_quarter+1]), 
                            (start_year-4, quarters[start_quarter+2]), 
                            (start_year-4, quarters[start_quarter+3]),
                            (start_year-3, quarters[start_quarter]), 
                            (start_year-3, quarters[start_quarter+1]), 
                            (start_year-3, quarters[start_quarter+2]), 
                            (start_year-3, quarters[start_quarter+3]), 
                            (start_year-2, quarters[start_quarter]), 
                            (start_year-2, quarters[start_quarter+1]), 
                            (start_year-2, quarters[start_quarter+2]), 
                            (start_year-2, quarters[start_quarter+3]), 
                            (start_year-1, quarters[start_quarter]), 
                            (start_year-1, quarters[start_quarter+1]), 
                            (start_year-1, quarters[start_quarter+2]), 
                            (start_year-1, quarters[start_quarter+3]), 
                            (start_year, quarters[start_quarter]), 
                            (start_year, quarters[start_quarter+1]), 
                            (start_year, quarters[start_quarter+2]), 
                            (start_year, quarters[start_quarter+3]), 
                            (end_year, quarters[end_quatrer-1]),
                            (end_year, quarters[end_quatrer])]
        elif current_quarter == 3:
            end_quatrer = 2
            end_year = current_year
            start_year = current_year - 1
            start_quarter = 0
            year_quarter = [(start_year-5, quarters[start_quarter]), 
                            (start_year-5, quarters[start_quarter+1]), 
                            (start_year-5, quarters[start_quarter+2]), 
                            (start_year-5, quarters[start_quarter+3]),
                            (start_year-4, quarters[start_quarter]), 
                            (start_year-4, quarters[start_quarter+1]), 
                            (start_year-4, quarters[start_quarter+2]), 
                            (start_year-4, quarters[start_quarter+3]),
                            (start_year-3, quarters[start_quarter]), 
                            (start_year-3, quarters[start_quarter+1]), 
                            (start_year-3, quarters[start_quarter+2]), 
                            (start_year-3, quarters[start_quarter+3]), 
                            (start_year-2, quarters[start_quarter]), 
                            (start_year-2, quarters[start_quarter+1]), 
                            (start_year-2, quarters[start_quarter+2]), 
                            (start_year-2, quarters[start_quarter+3]), 
                            (start_year-1, quarters[start_quarter]), 
                            (start_year-1, quarters[start_quarter+1]), 
                            (start_year-1, quarters[start_quarter+2]), 
                            (start_year-1, quarters[start_quarter+3]), 
                            (start_year, quarters[start_quarter]), 
                            (start_year, quarters[start_quarter+1]), 
                            (start_year, quarters[start_quarter+2]), 
                            (start_year, quarters[start_quarter+3]), 
                            (end_year, quarters[end_quatrer])]
        return year_quarter
    
    def convert_amount(x):
        if pd.isna(x):
            return x
        try:
            return int(str(x).replace(',', ''))
        except:
            return x
    
    
    def str_to_int(x):
        if pd.isna(x):
            return x
        if x == '-':
            return 0
        try:
            return int(str(x).replace(',', ''))
        except:
            return x
    
    def format_amount(x):
        if not x:  # None 체크
            return x
        if pd.isna(x):  # NaN 체크
            return x
            
        try:
            # 이미 숫자(float)인 경우
            if isinstance(x, (int, float)):
                value = float(x)
            # 문자열인 경우 쉼표 제거
            else:
                value = float(str(x).replace(',', ''))
                
            # 억 단위 변환
            value = value / 100000000
            
            # 소수점 2자리 반올림
            value = int(round(value, 0))
            # 천단위 콤마 추가
            return format(value, ',')
        except:
            return x
    
    
    year_quarter = get_year_quarter(current_quarter)
    q_reports_index = None
    q_reports = None
    for i, (_year, _quarters) in enumerate(year_quarter):
        # pprint(reports)
        quarter = str(_year) + '.' + str(_months[quarters.index(_quarters)]).zfill(2) + '.'
        # print('quarter:', quarter)
        # print('='*100)
        # if reports is not None:
        if reports is not None and i == 0:
            # print('reports=======:', reports)
            # q_reports_index = reports[['개별연결구분', '재무제표구분', '계정명']]
            if quarter in reports.columns:
                index_columns = ['개별연결구분', '재무제표구분', '계정명']
                q_reports = reports.set_index(index_columns)[[quarter]]
                # q_reports = reports[[quarter]]
                continue
            else:
                pass
        elif reports is not None and i != 0:
            if quarter in reports.columns:
                # 이후 데이터 병합
                temp_df = reports.set_index(index_columns)[[quarter]]
                
                # 기존 인덱스와 새 데이터의 인덱스를 동일한 형식으로 맞춤
                if not isinstance(q_reports.index, pd.MultiIndex):
                    q_reports = q_reports.set_index(index_columns)
                if not isinstance(temp_df.index, pd.MultiIndex):
                    temp_df = temp_df.set_index(index_columns)
                
                # 데이터프레임 병합
                q_reports = pd.concat([q_reports, temp_df], axis=1)
                continue
            else:
                pass
                
        # if reports is not None and i == len(year_quarter) - 1:
        #     q_reports_index = reports[['개별연결구분', '재무제표구분', '계정명']]
                    
        print(symbol, _year, _quarters)
        report = dart.finstate(corp=symbol, bsns_year=_year, reprt_code=_quarters)
        print(report)
        if not report.empty:
            pass
            # print('==============================================================')
            # print(report)
            # print(report[['account_nm', 'thstrm_amount']])
            # print(report.columns)
            # for col in report.columns:
            #     # if col in ['thstrm_amount', 'frmtrm_amount', 'bfefrmtrm_amount']:
            #     if 'amount' in col:
            #         report[col] = report[col].apply(convert_amount)
            # print(report[['account_nm', 'thstrm_amount']])
            # print('==============================================================')
            
        else:
            continue
        try:
            if '총포괄손익' not in report['account_nm'].values:
                # print(report)
                row_data = {}
                for col in report.columns:
                    row_data[col] = ''
                row_data['account_nm'] = '총포괄손익'
                
                # try:    
                row_data_1 = None
                row_data_2 = None
                # print('report fs_div:', report['fs_div'].values)
                row_data_1 = row_data.copy()
                row_data_1['fs_div'] = 'OFS'    # 'fs_div': '개별연결구분',   # (CFS=연결재무제표, OFS=재무제표)'
                row_data_1['sj_div'] = 'IS'     # 'sj_div': '재무제표구분',   # (BS=재무상태표, IS=손익계산서)'
                
                if '당기순이익' in report['account_nm'].values and 'OFS' in report['fs_div'].values:
                    row_data_1['thstrm_amount'] = report.loc[(report['account_nm'] == '당기순이익') & 
                                                            (report['fs_div'] == 'OFS'), 
                                                            'thstrm_amount'
                                                            ].values[0]
                else:
                    row_data_1['thstrm_amount'] = report.loc[(report['account_nm'] == '법인세차감전 순이익') & 
                                                            (report['fs_div'] == 'OFS'), 
                                                            'thstrm_amount'
                                                            ].values[0]

                if 'CFS' in report['fs_div'].values:
                    row_data_2 = row_data.copy()
                    row_data_2['fs_div'] = 'CFS'    # 'fs_div': '개별연결구분',   # (CFS=연결재무제표, OFS=재무제표)'
                    row_data_2['sj_div'] = 'IS'     # 'sj_div': '재무제표구분',   # (BS=재무상태표, IS=손익계산서)'
                    if '당기순이익' in report['account_nm'].values:
                        row_data_2['thstrm_amount'] = report.loc[(report['account_nm'] == '당기순이익') & 
                                                            (report['fs_div'] == 'CFS'), 
                                                            'thstrm_amount'
                                                            ].values[0]
                    else:
                        row_data_2['thstrm_amount'] = report.loc[(report['account_nm'] == '법인세차감전 순이익') & 
                                                            (report['fs_div'] == 'CFS'), 
                                                            'thstrm_amount'
                                                            ].values[0]
                    
                # print('row_data_1:', row_data_1)
                # print('row_data_2:', row_data_2)
                if row_data_2 is None:
                    report = pd.concat([
                        report.iloc[:14],
                        report.iloc[14:],
                        pd.DataFrame([row_data_1], columns=report.columns),
                    ]).reset_index(drop=True)
                else:
                    report = pd.concat([
                        report.iloc[:14],
                        pd.DataFrame([row_data_1], columns=report.columns),
                        report.iloc[14:],
                        pd.DataFrame([row_data_2], columns=report.columns),
                    ]).reset_index(drop=True)
                # except Exception as e:
                #     print('e:', e)
                #     row_data['account_nm'] = '총포괄손익'
                #     row_data_1 = row_data.copy()
                #     # row_data_1['fs_div'] = 'OFS'    # 'fs_div': '개별연결구분',   # (CFS=연결재무제표, OFS=재무제표)'
                #     row_data_1['sj_div'] = 'IS'     # 'sj_div': '재무제표구분',   # (BS=재무상태표, IS=손익계산서)'
                #     row_data_1['thstrm_amount'] = report.loc[(report['account_nm'] == '당기순이익'), 
                #                                             'thstrm_amount'
                #                                             ].values[0]
                #     report = pd.concat([
                #         report.iloc[:14],
                #         pd.DataFrame([row_data_1], columns=report.columns),
                #         report.iloc[14:],
                #     ]).reset_index(drop=True)
        except Exception as e:
            print('e:', e)
            pass
        if 'date' not in report['account_nm']:
            date = {}
            date['account_nm'] = 'date'
            date['thstrm_amount'] = report.iloc[1]['rcept_no'][:8]
            # print('date:', date)
            report = pd.concat([
                pd.DataFrame([date], columns=report.columns),
                report
            ]).reset_index(drop=True)
        
        
        report = report.rename(columns=column_name)
        # print(report.columns)
        # pprint(report[['계정명', '당기금액']])
        
        # report.loc[1:, '당기금액'] = report.loc[1:, '당기금액'].apply(format_amount)

        # report['당기금액'].iloc[1:] = report['당기금액'].iloc[1:].apply(format_amount)
        # report['전기금액'].iloc[1:] = report['전기금액'].iloc[1:].apply(format_amount)
        # pprint(report[['계정명', '당기금액']])
        
        q = ''
        if quarters.index(_quarters) == 0:
            q = str(_year) + '.03.'
        elif quarters.index(_quarters) == 1:
            q = str(_year) + '.06.'
        elif quarters.index(_quarters) == 2:
            q = str(_year) + '.09.'
        elif quarters.index(_quarters) == 3:
            q = str(_year) + '.12.'

        # print('q:', q)
        before_q = str(_year-1) + '.' + str(quarters.index(_quarters)+1) + '.'
        report = report.rename(columns={'당기금액': q, '전기금액': before_q})
        
        
        # 인덱스 컬럼 지정
        index_columns = ['개별연결구분', '재무제표구분', '계정명']

        if i == 0:
            # 첫 번째 데이터의 경우
            q_reports = report.set_index(index_columns)[[q]]
        else:
            # 이후 데이터 병합
            temp_df = report.set_index(index_columns)[[q]]
            
            # 기존 인덱스와 새 데이터의 인덱스를 동일한 형식으로 맞춤
            if not isinstance(q_reports.index, pd.MultiIndex):
                q_reports = q_reports.set_index(index_columns)
            if not isinstance(temp_df.index, pd.MultiIndex):
                temp_df = temp_df.set_index(index_columns)
            
            # 데이터프레임 병합
            q_reports = pd.concat([q_reports, temp_df], axis=1)

        # # 필요한 경우 인덱스 리셋
        # reports = q_reports.reset_index()
        
    
        time.sleep(0.07)
    # q_reports_index = q_reports_index.rename(columns={'계정명': '계정명.1'})
    
    # reports = pd.concat([q_reports_index, q_reports], axis=1)
    reports = q_reports
    reports = reports.reset_index()
    # print('==============================================================')
    # pprint(reports)
    # print('==============================================================')
    with get_redis_client() as redis_client:
        redis_client.set(f'{symbol}_balance_sheet', reports.to_json())
    
    year_report_columns = [column for column in reports.columns if column.endswith('.12.')]
    # print('year_report_columns:', year_report_columns)
    for column in year_report_columns:
        _year = column.split('.')[0]
        sales_cfs = 0
        profit_cfs_5 = 0
        profit_cfs_4 = 0
        profit_cfs_3 = 0
        profit_cfs_2 = 0
        profit_cfs_1 = 0
        sales_ofs = 0
        profit_ofs_5 = 0
        profit_ofs_4 = 0
        profit_ofs_3 = 0
        profit_ofs_2 = 0
        profit_ofs_1 = 0
        # try:
        for report in reports.columns:
            if report.startswith(_year) and not report.endswith('.12.'):
                # print('report:', reports.loc[(reports["개별연결구분"] == 'CFS') & 
                #                         (reports['계정명'] == '매출액'), report].values[0])
                # print('report:==========', reports)
                if 'CFS' in reports['개별연결구분'] and str_to_int(reports.loc[(reports["개별연결구분"] == 'CFS') and (reports['계정명'] == '매출액'), report].values[0]):
                    try:
                        sales_cfs += str_to_int(reports.loc[(reports["개별연결구분"] == 'CFS') & 
                                            (reports['계정명'] == '매출액'), report].values[0])
                    except:
                        sales_cfs = 0
                    
                    try:
                        profit_cfs_5 += str_to_int(reports.loc[(reports["개별연결구분"] == 'CFS') & 
                                            (reports['계정명'] == '영업이익'), report].values[0])
                    except:
                        profit_cfs_5 = 0
                    
                    try:
                        profit_cfs_4 += str_to_int(reports.loc[(reports["개별연결구분"] == 'CFS') & 
                                            (reports['계정명'] == '법인세차감전 순이익'), report].values[0])
                    except:
                        profit_cfs_4 = 0
                    
                    try:
                        profit_cfs_3 += str_to_int(reports.loc[(reports["개별연결구분"] == 'CFS') & 
                                            (reports['계정명'] == '당기순이익'), report].values[0])
                    except:
                        profit_cfs_3 = 0
                    
                    try:
                        profit_cfs_2 += str_to_int(reports.loc[(reports["개별연결구분"] == 'CFS') & 
                                            (reports['계정명'] == '당기순이익(손실)'), report].values[0])
                    except:
                        profit_cfs_2 = 0
                    
                    try:
                        profit_cfs_1 += str_to_int(reports.loc[(reports["개별연결구분"] == 'CFS') & 
                                            (reports['계정명'] == '총포괄손익'), report].values[0])
                    except:
                        profit_cfs_1 = 0
                    
                
                sales_ofs += str_to_int(reports.loc[(reports["개별연결구분"] == 'OFS') & 
                                        (reports['계정명'] == '매출액'), report].values[0])
                
                profit_ofs_5 += str_to_int(reports.loc[(reports["개별연결구분"] == 'OFS') & 
                                        (reports['계정명'] == '영업이익'), report].values[0])
                
                profit_ofs_4 += str_to_int(reports.loc[(reports["개별연결구분"] == 'OFS') & 
                                        (reports['계정명'] == '법인세차감전 순이익'), report].values[0])
                
                # print('당기순이익:',str_to_int(reports.loc[(reports["개별연결구분"] == 'OFS') & 
                #                         (reports['계정명'] == '당기순이익'), report].values[0]))
                try:
                    profit_ofs_3 += str_to_int(reports.loc[(reports["개별연결구분"] == 'OFS') & 
                                            (reports['계정명'] == '당기순이익'), report].values[0])
                except:
                    profit_ofs_3 = 0
                
                try:
                    profit_ofs_2 += str_to_int(reports.loc[(reports["개별연결구분"] == 'OFS') & 
                                            (reports['계정명'] == '당기순이익(손실)'), report].values[0])
                except:
                    profit_ofs_2 = 0
                
                # print(reports.loc[(reports["개별연결구분"] == 'OFS') & 
                #                         (reports['계정명'] == '총포괄손익'), report].values[0])

                try:
                    profit_ofs_1 += str_to_int(reports.loc[(reports["개별연결구분"] == 'OFS') & 
                                            (reports['계정명'] == '총포괄손익'), report].values[0])
                except:
                    profit_ofs_1 = 0
                
        if 'CFS' in reports['개별연결구분'] and '매출액' in reports['계정명']:
            
            reports.loc[(reports["개별연결구분"] == 'CFS' ) & (reports['계정명'] == '매출액'), column] = format(str_to_int(reports.loc[(reports["개별연결구분"] == 'CFS') &
                                                                                (reports['계정명'] == '매출액'), column].values[0]) - sales_cfs, ',')
            
            reports.loc[(reports["개별연결구분"] == 'CFS' ) & (reports['계정명'] == '영업이익'), column] = format(str_to_int(reports.loc[(reports["개별연결구분"] == 'CFS') &
                                                                                (reports['계정명'] == '영업이익'), column].values[0]) - profit_cfs_5, ',')
            
            reports.loc[(reports["개별연결구분"] == 'CFS' ) & (reports['계정명'] == '법인세차감전 순이익'), column] = format(str_to_int(reports.loc[(reports["개별연결구분"] == 'CFS') &
                                                                                (reports['계정명'] == '법인세차감전 순이익'), column].values[0]) - profit_cfs_4, ',')
            
            reports.loc[(reports["개별연결구분"] == 'CFS' ) & (reports['계정명'] == '당기순이익'), column] = format(str_to_int(reports.loc[(reports["개별연결구분"] == 'CFS') &
                                                                                (reports['계정명'] == '당기순이익'), column].values[0]) - profit_cfs_3, ',')
            
            reports.loc[(reports["개별연결구분"] == 'CFS' ) & (reports['계정명'] == '당기순이익(손실)'), column] = format(str_to_int(reports.loc[(reports["개별연결구분"] == 'CFS') &
                                                                                (reports['계정명'] == '당기순이익(손실)'), column].values[0]) - profit_cfs_2, ',')
            
            reports.loc[(reports["개별연결구분"] == 'CFS' ) & (reports['계정명'] == '총포괄손익'), column] = format(str_to_int(reports.loc[(reports["개별연결구분"] == 'CFS') &
                                                                                (reports['계정명'] == '총포괄손익'), column].values[0]) - profit_cfs_1, ',')
        
        reports.loc[(reports["개별연결구분"] == 'OFS' ) & (reports['계정명'] == '매출액'), column] = format(str_to_int(reports.loc[(reports["개별연결구분"] == 'OFS') &
                                                                            (reports['계정명'] == '매출액'), column].values[0]) - sales_ofs, ',')
        
        reports.loc[(reports["개별연결구분"] == 'OFS' ) & (reports['계정명'] == '영업이익'), column] = format(str_to_int(reports.loc[(reports["개별연결구분"] == 'OFS') &
                                                                            (reports['계정명'] == '영업이익'), column].values[0]) - profit_ofs_5, ',')
        
        reports.loc[(reports["개별연결구분"] == 'OFS' ) & (reports['계정명'] == '법인세차감전 순이익'), column] = format(str_to_int(reports.loc[(reports["개별연결구분"] == 'OFS') &
                                                                            (reports['계정명'] == '법인세차감전 순이익'), column].values[0]) - profit_ofs_4, ',')
        
        try:
            reports.loc[(reports["개별연결구분"] == 'OFS' ) & (reports['계정명'] == '당기순이익'), column] = format(str_to_int(reports.loc[(reports["개별연결구분"] == 'OFS') &
                                                                            (reports['계정명'] == '당기순이익'), column].values[0]) - profit_ofs_3, ',')
        except:
            reports.loc[(reports["개별연결구분"] == 'OFS' ) & (reports['계정명'] == '당기순이익'), column] = 0
        
        try:
            reports.loc[(reports["개별연결구분"] == 'OFS' ) & (reports['계정명'] == '당기순이익(손실)'), column] = format(str_to_int(reports.loc[(reports["개별연결구분"] == 'OFS') &
                                                                            (reports['계정명'] == '당기순이익(손실)'), column].values[0]) - profit_ofs_2, ',')
        except:
            reports.loc[(reports["개별연결구분"] == 'OFS' ) & (reports['계정명'] == '당기순이익(손실)'), column] = 0

        try:            
            reports.loc[(reports["개별연결구분"] == 'OFS' ) & (reports['계정명'] == '총포괄손익'), column] = format(str_to_int(reports.loc[(reports["개별연결구분"] == 'OFS') &
                                                                                (reports['계정명'] == '총포괄손익'), column].values[0]) - profit_ofs_1, ',')
        except:
            reports.loc[(reports["개별연결구분"] == 'OFS' ) & (reports['계정명'] == '총포괄손익'), column] = 0
        # except Exception as e:
        #     print('e:', e)
        #     for report in reports.columns:
        #         if report.startswith(_year) and not report.endswith('.12.'):
        #             # print('report:', reports.loc[(reports["개별연결구분"] == 'CFS') & 
        #             #                         (reports['계정명'] == '매출액'), report].values[0])
                    
        #             sales_cfs += str_to_int(reports.loc[(reports['계정명'] == '매출액'), report].values[0])
                    
        #             profit_cfs_5 += str_to_int(reports.loc[(reports['계정명'] == '영업이익'), report].values[0])
                    
        #             profit_cfs_4 += str_to_int(reports.loc[(reports['계정명'] == '법인세차감전 순이익'), report].values[0])
                    
        #             try:
        #                 profit_cfs_3 += str_to_int(reports.loc[(reports['계정명'] == '당기순이익'), report].values[0])
        #             except:
        #                 profit_cfs_3 = 0
                    
        #             try:
        #                 profit_cfs_2 += str_to_int(reports.loc[(reports['계정명'] == '당기순이익(손실)'), report].values[0])
        #             except:
        #                 profit_cfs_2 = 0
                    
        #             try:
        #                 profit_cfs_1 += str_to_int(reports.loc[(reports['계정명'] == '총포괄손익'), report].values[0])
        #             except:
        #                 profit_cfs_1 = 0
                    
        #             sales_ofs += str_to_int(reports.loc[(reports['계정명'] == '매출액'), report].values[0])
                    
        #             profit_ofs_5 += str_to_int(reports.loc[(reports['계정명'] == '영업이익'), report].values[0])
                    
        #             profit_ofs_4 += str_to_int(reports.loc[(reports['계정명'] == '법인세차감전 순이익'), report].values[0])
                    
        #             try:
        #                 profit_ofs_3 += str_to_int(reports.loc[(reports['계정명'] == '당기순이익'), report].values[0])
        #             except:
        #                 profit_ofs_3 = 0
                    
        #             try:
        #                 profit_ofs_2 += str_to_int(reports.loc[(reports['계정명'] == '당기순이익(손실)'), report].values[0])
        #             except:
        #                 profit_ofs_2 = 0
                    
        #             try:
        #                 profit_ofs_1 += str_to_int(reports.loc[(reports['계정명'] == '총포괄손익'), report].values[0])
        #             except:
        #                 profit_ofs_1 = 0
        #         print('profit_ofs_1:', profit_ofs_1)
        #         # for col in reports.columns:
        #         #     if col.startswith('20'):
        #         #         print(col, reports[['계정명', col]])
        #         #         reports[col] = pd.to_numeric(reports[col].replace(',', ''), errors='coerce')
        #         if report.startswith(_year) and report.endswith('.12.'):
        #             reports.loc[(reports['계정명'] == '매출액'), column] = format(str_to_int(reports.loc[(reports['계정명'] == '매출액'), column].values[0]) - sales_ofs, ',')
                    
        #             reports.loc[(reports['계정명'] == '영업이익'), column] = format(str_to_int(reports.loc[(reports['계정명'] == '영업이익'), column].values[0]) - profit_ofs_5, ',')
                    
        #             reports.loc[(reports['계정명'] == '법인세차감전 순이익'), column] = format(str_to_int(reports.loc[(reports['계정명'] == '법인세차감전 순이익'), column].values[0]) - profit_ofs_4, ',')
                    
                    
        #             try:
        #                 reports.loc[(reports['계정명'] == '당기순이익'), column] = format(str_to_int(reports.loc[(reports['계정명'] == '당기순이익'), column].values[0]) - profit_ofs_3, ',')
        #             except:
        #                 reports.loc[(reports['계정명'] == '당기순이익'), column] = ''
                    
        #             try:
        #                 reports.loc[(reports['계정명'] == '당기순이익(손실)'), column] = format(str_to_int(reports.loc[(reports['계정명'] == '당기순이익(손실)'), column].values[0]) - profit_ofs_2, ',')
        #             except:
        #                 reports.loc[(reports['계정명'] == '당기순이익(손실)'), column] = ''
                    
        #             try:
        #                 reports.loc[(reports['계정명'] == '총포괄손익'), column] = format(str_to_int(reports.loc[(reports['계정명'] == '총포괄손익'), column].values[0]) - profit_ofs_1, ',')
        #             except:
        #                 reports.loc[(reports['계정명'] == '총포괄손익'), column] = ''
            
            # reports.loc[(reports['계정명'] == '매출액'), column] = format(str_to_int(reports.loc[(reports['계정명'] == '매출액'), column].values[0]) - sales_ofs, ',')
            
            # reports.loc[(reports['계정명'] == '영업이익'), column] = format(str_to_int(reports.loc[(reports['계정명'] == '영업이익'), column].values[0]) - profit_ofs_5, ',')
            
            # reports.loc[(reports['계정명'] == '법인세차감전 순이익'), column] = format(str_to_int(reports.loc[(reports['계정명'] == '법인세차감전 순이익'), column].values[0]) - profit_ofs_4, ',')
            
            # reports.loc[(reports['계정명'] == '당기순이익'), column] = format(str_to_int(reports.loc[(reports['계정명'] == '당기순이익'), column].values[0]) - profit_ofs_3, ',')
            
            # reports.loc[(reports['계정명'] == '당기순이익(손실)'), column] = format(str_to_int(reports.loc[(reports['계정명'] == '당기순이익(손실)'), column].values[0]) - profit_ofs_2, ',')
            
            # reports.loc[(reports['계정명'] == '총포괄손익'), column] = format(str_to_int(reports.loc[(reports['계정명'] == '총포괄손익'), column].values[0]) - profit_ofs_1, ',')

            # reports = reports.drop(columns=['개별연결구분', '재무제표구분'])
            
    # 데이터프레임을 딕셔너리로 변환하기 전에 기본 타입으로 변환
    def convert_to_basic_types(obj):
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient='records')
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj       
    print('+++++++++++++++++++++++++++')
    reports = reports.where(pd.notnull(reports), None)
    
    # reports = convert_to_basic_types(reports)
    pprint(reports)
    # print('+++++++++++++++++++++++++++')
    
    
    
    return reports
    






    

def get_report_by_key_word(symbol, key_word):
    print(symbol)
    current_year = datetime.now().year
    _years = [current_year - i for i in range(5)]
    _years.reverse()
    print(_years)
    '''
    key_word 항목목
    1.	'증자'	증자(감자) 현황	
    2.	'배당'	배당에 관한 사항	
    3.	'자기주식'	자기주식 취득 및 처분 현황	
    4.	'최대주주'	최대주주 현황	
    5.	'최대주주변동'	최대주주 변동 현황	
    6.	'소액주주'	소액주주현황	
    7.	'임원'	임원현황	
    8.	'직원'	직원현황	
    9.	'임원개인보수'	이사ㆍ감사의 개인별 보수 현황	
    10.	'임원전체보수'	이사ㆍ감사 전체의 보수현황	
    11.	'개인별보수'	개인별 보수지급 금액(5억이상 상위5인)	
    12.	'타법인출자'	타법인 출자현황
    '''
    report = dart.report(corp=symbol, key_word=key_word, bsns_year=_years[0], reprt_code='11011')
    print(report)
    # report = dart.company(symbol)
    # report = dart.report(symbol, '배당', 2024)
    # report = dart.list(symbol, 2024)
    
    pass

def is_empty_report(report):
    if report.empty:
        return True
    else:
        return False

def find_fins_ind_list(stock_code, stock_name, year, ind_list):
    try: # 데이터 가져오기
        report = None
        report = dart.finstate(stock_code, year)  # 스탁코드와 연도
    except:
        pass
    
    # print('report:', report)
    
    for i in range(3):
        report = None
        year = year - i
        report = dart.finstate(stock_code, year)
        if not report.empty:
            break
        time.sleep(0.07)
    # print('report:', report)
    
    if report is None:  # 리포트가 없다면 (참고: 리포트가 없으면 None을 반환함)
        # 리포트가 없으면 당기, 전기, 전전기 값 모두 제거
        data = [[stock_name, year] + [np.nan] * len(ind_list)] # 당기
        data.append([stock_name, year - 1] + [np.nan] * len(ind_list)) # 전기
        data.append([stock_name, year - 2] + [np.nan] * len(ind_list)) # 전전기
        data.append([stock_name, year - 3] + [np.nan] * len(ind_list)) # 전전전기
    
    else:
        report = report[report["account_nm"].isin(ind_list)]  # 관련 지표로 필터링
        if sum(report["fs_nm"] == "연결재무제표") > 0:
            # 연결재무제표 데이터가 있으면 연결재무제표를 사용
            report = report.loc[report["fs_nm"] == "연결재무제표"]
        else:
            # 연결재무제표 데이터가 없으면 일반재무제표를 사용 (그냥 제무제표)
            report = report.loc[report["fs_nm"] == "재무제표"] #
        data = []
        for y, c in zip([year, year - 1, year - 2, year - 3],  #2023 ~ 2021
                        ["thstrm_amount", "frmtrm_amount", "bfefrmtrm_amount"]): #자산, 부채, 자본총계
            record = [stock_name, y] #스탁코드, 연도
            for ind in ind_list:
                # account_nm이 indic인 행의 c 컬럼 값을 가져옴
                if sum(report["account_nm"] == ind) > 0: # 기수별 당기순이익의 총합으로 계산해야 함
                    value = report.loc[report["account_nm"] == ind, c].iloc[0]
                else:
                    value = np.nan
                record.append(value)
            data.append(record)
            time.sleep(0.07)
    
    return pd.DataFrame(data, columns=["기업", "연도"] + ind_list) # 한 프레임에 담기 위해 + 사용


