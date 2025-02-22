from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date
from app.db.session import get_asset_db
from app.schemas import investment_schemas_v3 as schemas
from app.crud.v3 import accounts as crud

router = APIRouter()


@router.post("/initialize", response_model=Dict[str, Any])
async def initialize_default_accounts(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_asset_db)
):
    """기본 계정과목 초기화"""
    default_accounts = [
        # 자산 계정
        {"code": "1000", "name": "자산", "account_type": "ASSET", "parent_id": None},
        {"code": "1100", "name": "현금성자산", "account_type": "ASSET", "parent_id": "1000"},
        {"code": "1110", "name": "현금", "account_type": "ASSET", "parent_id": "1100"},
        {"code": "1120", "name": "보통예금", "account_type": "ASSET", "parent_id": "1100"},
        {"code": "1130", "name": "정기예금", "account_type": "ASSET", "parent_id": "1100"},
        
        {"code": "1200", "name": "투자자산", "account_type": "ASSET", "parent_id": "1000"},
        {"code": "1210", "name": "주식", "account_type": "ASSET", "parent_id": "1200"},
        {"code": "1220", "name": "채권", "account_type": "ASSET", "parent_id": "1200"},
        {"code": "1230", "name": "펀드", "account_type": "ASSET", "parent_id": "1200"},
        {"code": "1240", "name": "암호화폐", "account_type": "ASSET", "parent_id": "1200"},
        
        # 부채 계정
        {"code": "2000", "name": "부채", "account_type": "LIABILITY", "parent_id": None},
        {"code": "2100", "name": "대출금", "account_type": "LIABILITY", "parent_id": "2000"},
        {"code": "2200", "name": "미지급금", "account_type": "LIABILITY", "parent_id": "2000"},
        
        # 자본 계정
        {"code": "3000", "name": "자본", "account_type": "EQUITY", "parent_id": None},
        {"code": "3100", "name": "원금", "account_type": "EQUITY", "parent_id": "3000"},
        {"code": "3200", "name": "미실현손익", "account_type": "EQUITY", "parent_id": "3000"},
        {"code": "3300", "name": "이익잉여금", "account_type": "EQUITY", "parent_id": "3000"},
        
        # 수익 계정
        {"code": "4000", "name": "수익", "account_type": "INCOME", "parent_id": None},
        {"code": "4100", "name": "이자수익", "account_type": "INCOME", "parent_id": "4000"},
        {"code": "4110", "name": "예금이자", "account_type": "INCOME", "parent_id": "4100"},
        {"code": "4120", "name": "채권이자", "account_type": "INCOME", "parent_id": "4100"},
        
        {"code": "4200", "name": "배당수익", "account_type": "INCOME", "parent_id": "4000"},
        {"code": "4300", "name": "매매차익", "account_type": "INCOME", "parent_id": "4000"},
        {"code": "4400", "name": "환차익", "account_type": "INCOME", "parent_id": "4000"},
        
        # 비용 계정
        {"code": "5000", "name": "비용", "account_type": "EXPENSE", "parent_id": None},
        {"code": "5100", "name": "수수료비용", "account_type": "EXPENSE", "parent_id": "5000"},
        {"code": "5110", "name": "매매수수료", "account_type": "EXPENSE", "parent_id": "5100"},
        {"code": "5120", "name": "계좌수수료", "account_type": "EXPENSE", "parent_id": "5100"},
        
        {"code": "5200", "name": "이자비용", "account_type": "EXPENSE", "parent_id": "5000"},
        {"code": "5300", "name": "매매차손", "account_type": "EXPENSE", "parent_id": "5000"},
        {"code": "5400", "name": "환차손", "account_type": "EXPENSE", "parent_id": "5000"},
    ]

    # try:
    # 기존 계정 초기화 (선택적)
    background_tasks.add_task(crud.reset_accounts, db)
    
    # 기본 계정 생성
    result = await crud.create_default_accounts(db, default_accounts)
    
    return {
        "status": "success",
        "message": "기본 계정과목이 초기화되었습니다.",
        "created_count": len(result)
    }
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500,
    #         detail=f"계정과목 초기화 중 오류가 발생했습니다: {str(e)}"
    #     )