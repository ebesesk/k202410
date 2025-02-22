import datetime

def get_today():
    return datetime.datetime.now().strftime('%Y-%m-%d')

def get_ten_days_ago(date=None):
    if date:
        return (datetime.datetime.strptime(date, '%Y-%m-%d') - datetime.timedelta(days=10)).strftime('%Y-%m-%d')
    else:
        return (datetime.datetime.now() - datetime.timedelta(days=10)).strftime('%Y-%m-%d')