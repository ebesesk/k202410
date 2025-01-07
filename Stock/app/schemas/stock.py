from pydantic import BaseModel, Field
from typing import Optional, Annotated


class InterestStock(BaseModel):
    
    종목코드: Optional[Annotated[str, Field(min_length=6, max_length=6)]] = None  # 6자리로 제한
    한글기업명: Optional[str] = None
    시장구분: Optional[str] = None
    업종구분명: Optional[str] = None
    tag: Optional[str] = None
    username: Optional[str] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True
        

class InterestStockCodes(BaseModel):
    codes: list[Annotated[str, Field(min_length=6, max_length=6)]]  # 리스트의 각 코드도 6자리로 제한

class InterestStockInput(BaseModel):
    key: Optional[str] = None
    code: Optional[str] = None

class InterestStockTag(BaseModel):
    종목코드: Optional[Annotated[str, Field(min_length=6, max_length=6)]] = None
    tag: Optional[str] = None
    username: Optional[str] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True


class AppKey(BaseModel):
    appkey: Optional[str] = None
    appsecretkey: Optional[str] = None
    cname: Optional[str] = None
    username: Optional[str] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True
        
class AppKeyRequest(BaseModel):
    cname: str
    username: str


# class ChartData(BaseModel):
#     shcode: str
#     chart_data: dict
#     date: str
#     period: str
#     username: str

#     class Config:
#         from_attributes = True
#         populate_by_name = True
        
# class ChartDataRequest(BaseModel):
#     shcode: str
#     period: str
#     date: str
#     username: str

# class ChartDataDelete(BaseModel):
#     shcode: str
#     period: str
#     date: str
#     username: str

# class ChartDataResponse(BaseModel):
#     chart: dict

