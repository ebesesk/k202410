from pydantic import BaseModel, Field
from typing import Optional

class ApartmentTransaction(BaseModel):
    sggCd: Optional[str] = Field(None, alias='법정동시군구코드')
    umdCd: Optional[str] = Field(None, alias='법정동읍면동코드')
    landCd: Optional[str] = Field(None, alias='법정동지번코드')
    bonbun: Optional[str] = Field(None, alias='법정동본번코드')
    bubun: Optional[str] = Field(None, alias='법정동부번코드')
    roadNm: Optional[str] = Field(None, alias='도로명')
    roadNmSggCd: Optional[str] = Field(None, alias='도로명시군구코드')
    roadNmCd: Optional[str] = Field(None, alias='도로명코드')
    roadNmSeq: Optional[str] = Field(None, alias='도로명일련번호코드')
    roadNmbCd: Optional[str] = Field(None, alias='도로명지상지하코드')
    roadNmBonbun: Optional[str] = Field(None, alias='도로명건물본번호코드')
    roadNmBubun: Optional[str] = Field(None, alias='도로명건물부번호코드')
    umdNm: Optional[str] = Field(None, alias='법정동')
    aptNm: Optional[str] = Field(None, alias='단지명')
    jibun: Optional[str] = Field(None, alias='지번')
    excluUseAr: Optional[float] = Field(None, alias='전용면적')
    dealYear: Optional[str] = Field(None, alias='계약년도')
    dealMonth: Optional[str] = Field(None, alias='계약월')
    dealDay: Optional[str] = Field(None, alias='계약일')
    dealAmount: Optional[str] = Field(None, alias='거래금액')
    floor: Optional[str] = Field(None, alias='층')
    buildYear: Optional[str] = Field(None, alias='건축년도')
    aptSeq: Optional[str] = Field(None, alias='단지일련번호')
    cdealType: Optional[str] = Field(None, alias='해제여부')
    cdealDay: Optional[str] = Field(None, alias='해제사유발생일')
    dealingGbn: Optional[str] = Field(None, alias='거래유형')
    estateAgentSggNm: Optional[str] = Field(None, alias='중개사소재지')
    rgstDate: Optional[str] = Field(None, alias='등기일자')
    aptDong: Optional[str] = Field(None, alias='아파트동명')
    slerGbn: Optional[str] = Field(None, alias='매도자')
    buyerGbn: Optional[str] = Field(None, alias='매수자')
    landLeaseholdGbn: Optional[str] = Field(None, alias='토지임대부아파트여부')

    class Config:
        from_attributes = True
        populate_by_name = True