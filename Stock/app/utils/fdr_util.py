import FinanceDataReader as fdr
from app.utils.date_util import get_ten_days_ago, get_today
from app.utils import utils
from sqlalchemy.orm import Session

def get_fdr_price_ten_days(symbol, date=None):
    # print('get_fdr_price_ten_days:', symbol)
    # print('get_today():', get_today())
    if date:
        # print('symbol:', symbol)
        # print('get_ten_days_ago():', get_ten_days_ago(date))
        # print('date:', date)
        return fdr.DataReader(symbol, get_ten_days_ago(date), date)
    else:
        return fdr.DataReader(symbol, get_ten_days_ago(), get_today())

def get_fdr_price(db:Session, codes, date=None):
    # print('codes:', codes)
    fdr_data = {}
    if isinstance(codes, str):
        codes = (codes+',').split(',')
    codes.remove('')    # 빈 문자열 제거
    # print('codes:', codes)
    if not codes:
        return {}
    for code in codes:
        try:
            market = utils.check_symbol(db, code.upper())
        except Exception as e:
            # print('e:', e)
            pass
        # if not market:
        #     pass
        fdr_data[code] = get_fdr_price_ten_days(code, date)
        # print('fdr_data[code]', fdr_data[code])
        price = fdr_data[code].iloc[-1]['Close']
        fdr_data[code] = price
        print('fdr_price:', code, fdr_data[code])
    return fdr_data