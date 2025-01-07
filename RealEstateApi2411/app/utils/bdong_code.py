import os, sys, requests
import PublicDataReader as pdr

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from core.config import settings

class Bdongcode:
    def __init__(self):
        self.api_key = settings.API_KEY
        self.api = pdr.Fred(api_key=self.api_key)
        self.bdong_df = pdr.code_bdong()
    
    def get_sido(self):
        sido = self.bdong_df[['시도코드', '시도명']].drop_duplicates(subset=['시도명']).values.tolist()
        제외할_지역 = ['강원도', '제주특별자치도', '전라북도']
        sido = [s for s in sido if s[1] not in 제외할_지역]
        sido.sort(key=lambda x: x[1])
        return sido
    
    def get_sigungu(self, sido_code):
        sigungu = self.bdong_df.loc[self.bdong_df['시도코드'] == sido_code][['시군구코드', '시군구명']]\
            .drop_duplicates(subset=['시군구코드']).values.tolist()
        print(sigungu)
        sigungu.sort(key=lambda x: x[1])
        return sigungu
    
    def get_dongli(self, sigungu_code):
        dong = self.bdong_df.loc[self.bdong_df['시군구코드'] == sigungu_code][['법정동코드', '읍면동명', '동리명']]\
            .drop_duplicates(subset=['법정동코드']).values.tolist()
        dong_list = []
        for d in dong:
            if d[2] == '':
                dong_list.append([d[0], d[1]])
            else:
                dong_list.append([d[0], d[1]+' '+d[2]])
        dong_list.sort(key=lambda x: x[1])
        return dong_list

if __name__ == '__main__':
    apt_util = Bdongcode()
    print('-'*100)
    print(apt_util.get_sido())
    print('-'*100)
    print(apt_util.get_sigungu('51'))
    print('-'*100)
    print(apt_util.get_dongli('51150'))