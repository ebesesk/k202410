from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.models.investment_models_v3 import Account

async def create_default_accounts(db: Session, accounts: List[Dict[str, Any]]) -> List[Account]:
    """기본 계정과목 생성"""
    created_accounts = []
    code_to_id = {}  # 코드와 ID 매핑을 위한 딕셔너리

    # 첫 번째 패스: 모든 계정 생성 (parent_id 없이)
    for account_data in accounts:
        account = Account()
        account.code = account_data["code"]
        account.name = account_data["name"]
        account.account_type = account_data["account_type"]
        
        db.add(account)
        db.flush()  # ID 생성을 위해 flush
        code_to_id[account.code] = account.id
        created_accounts.append(account)

    # 두 번째 패스: parent_id 업데이트
    for account, account_data in zip(created_accounts, accounts):
        if account_data["parent_id"]:
            account.parent_id = code_to_id[account_data["parent_id"]]

    db.commit()
    return created_accounts

async def reset_accounts(db: Session) -> None:
    """모든 계정과목 삭제"""
    try:
        db.query(Account).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        raise e