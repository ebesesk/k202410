from datetime import datetime, timedelta

class DateUtils:
    """날짜 관련 유틸리티 클래스"""
    
    @staticmethod
    def get_current_date():
        """현재 날짜를 반환합니다."""
        return datetime.now().strftime("%Y%m")
    
    @staticmethod
    def get_1_month_ago_date(date='202410'):
        """1달 전 날짜를 반환합니다."""
        return (datetime.strptime(date, "%Y%m") - timedelta(days=30)).strftime("%Y%m")
    
    @staticmethod
    def get_3_month_ago_date(date='202410'):
        """3달 전 날짜를 반환합니다."""
        return (datetime.strptime(date, "%Y%m") - timedelta(days=60)).strftime("%Y%m")
    
    @staticmethod
    def get_1_year_ago_date(date='202410'):
        """1년 전 날짜를 반환합니다."""
        return (datetime.now() - timedelta(days=365)).strftime("%Y%m")
    
    @staticmethod
    def get_3_year_ago_date(date='202410'):
        """5년 전 날짜를 반환합니다."""
        return (datetime.strptime(date, "%Y%m") - timedelta(days=1095)).strftime("%Y%m")
    
    @staticmethod
    def get_5_year_ago_date(date='202410'):
        """5년 전 날짜를 반환합니다."""
        return (datetime.strptime(date, "%Y%m") - timedelta(days=1825)).strftime("%Y%m")
    
    @staticmethod
    def get_10_year_ago_date(date='202410'):
        """10년 전 날짜를 반환합니다."""
        return (datetime.strptime(date, "%Y%m") - timedelta(days=3650)).strftime("%Y%m")
    
    @staticmethod
    def to_list(date1='201410', date2='202410'):
        """날짜 기간을 리스트로 반환합니다."""
        month_diff = (int(date2[:4]) - int(date1[:4])) * 12 + (int(date2[4:]) - int(date1[4:]))
        date_list = []
        
        for i in range(month_diff):
            month = (int(date1[4:]) + i) % 12 + 1
            year = int(date1[:4]) + (int(date1[4:]) + i) // 12
            date_list.append(f"{year}{month:02d}")
        
        return date_list

if __name__ == '__main__':
    now = DateUtils.get_current_date()
    three_month_ago = DateUtils.get_3_month_ago_date(now)
    ten_year_ago = DateUtils.get_10_year_ago_date(now)
    print(DateUtils.to_list(ten_year_ago, three_month_ago))