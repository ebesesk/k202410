from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import date
from app.utils.bdong_code import Bdongcode
# FastApi202410 경로를 수정
from app.utils.dependencies import get_current_user  # 경로 수정
from app.schemas.bdong_code import BdongCodeResponse, BdongCodeItem

router = APIRouter()


@router.get("/sido")
async def get_sido(current_user = Depends(get_current_user)):
    """시도 코드 조회"""
    print(current_user)
    apt_util = Bdongcode()
    sido_list = apt_util.get_sido()
    # 리스트를 딕셔너리 리스트로 변환
    sido_dict_list = [{"code": code, "name": name} for code, name in sido_list]
    print(sido_dict_list)
    return BdongCodeResponse(message=sido_dict_list)

@router.get("/sigungu")
async def get_sigungu(sido_code: str, current_user = Depends(get_current_user)):
    """시군구 코드 조회"""
    apt_util = Bdongcode()
    sigungu_list = apt_util.get_sigungu(sido_code)
    # 리스트를 딕셔너리 리스트로 변환
    sigungu_dict_list = [{"code": code, "name": name} for code, name in sigungu_list]
    return BdongCodeResponse(message=sigungu_dict_list)

@router.get("/dongli")
async def get_dongli(sigungu_code: str, current_user = Depends(get_current_user)):
    """동리 코드 조회"""
    apt_util = Bdongcode()
    dongli_list = apt_util.get_dongli(sigungu_code)
    # 리스트를 딕셔너리 리스트로 변환
    dongli_dict_list = [{"code": code, "name": name} for code, name in dongli_list]
    return BdongCodeResponse(message=dongli_dict_list)

# @router.get("/transactions")
# async def get_transactions(
#     current_user = Depends(get_current_user),
#     dong: Optional[str] = None,  # 동 이름
#     apt_name: Optional[str] = None,  # 아파트명
#     start_date: Optional[date] = None,
#     end_date: Optional[date] = None,
#     min_price: Optional[int] = None,
#     max_price: Optional[int] = None,
#     min_area: Optional[float] = None,  # 전용면적
#     max_area: Optional[float] = None
# ):
#     """아파트 실거래가 목록 조회"""
#     return {"message": "실거래가 목록"}

# @router.get("/complexes")
# async def get_apt_complexes(
#     current_user = Depends(get_current_user),
#     dong: Optional[str] = None
# ):
#     """아파트 단지 목록 조회"""
#     return {"message": "아파트 단지 목록"}

# @router.get("/statistics/monthly")
# async def get_monthly_stats(
#     current_user = Depends(get_current_user),
#     dong: Optional[str] = None,
#     apt_name: Optional[str] = None,
#     year: int,
#     month: int
# ):
#     """월별 실거래가 통계"""
#     return {"message": "월별 통계"}