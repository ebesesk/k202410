import os
from dotenv import load_dotenv
import json
# .env 파일 로드
load_dotenv()

class Settings:
    
    # 인증 서버 URL 설정
    AUTH_SERVER_URL: str = os.getenv("AUTH_SERVER_URL")
    
    # 오픈 API 키 설정
    OPEN_API_KEY: str = os.getenv("OPEN_API_KEY")
    
    # 해외 API 키 설정
    OVERSEA_API_KEY: str = os.getenv("OVERSEA_API_KEY")
    
    # 결과 파일 경로 설정
    RES_PATH: str = os.getenv("RES_PATH")
    
    # 토큰 파일 경로 설정
    TOKEN_FILE: str = os.getenv("TOKEN_FILE")
    OVERSEA_TOKEN_FILE: str = os.getenv("OVERSEA_TOKEN_FILE")
    
    # 도메인 설정
    DOMAIN: str = os.getenv("DOMAIN")
    
    # KIS 한투 도메인 설정
    KIS_DOMAIN: str = os.getenv("KIS_DOMAIN")
    KIS_TOKEN_FILE: str = os.getenv("KIS_TOKEN_FILE")
    KIS_ACCOUNT: str = os.getenv("KIS_ACCOUNT")
    # 웹소켓 URL 설정
    WEBSOCKET_URL: str = os.getenv("WEBSOCKET_URL")
    
    # 데이터베이스 설정
    SQLALCHEMY_DATABASE_URL: str = os.getenv("SQLALCHEMY_DATABASE_URL")
    INVESTMENT_DATABASE_URL: str = os.getenv("INVESTMENT_DATABASE_URL")
    ASSET_DATABASE_URL: str = os.getenv("ASSET_DATABASE_URL")
    
    # 앱 설정
    APP_NAME: str = os.getenv("APP_NAME")
    APP_VERSION: str = os.getenv("APP_VERSION")
    
    # CORS 설정
    CORS_ORIGINS: list = [
        "https://k2410.ebesesk.synology.me"
    ]
    
    # 레디스 설정
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT"))
    REDIS_DB: int = int(os.getenv("REDIS_DB"))
    
    # 증권 중계 수수료 세금
    COMMISSION_RATE_STOCK_KR: float = float(os.getenv("COMMISSION_RATE_STOCK_KR"))
    COMMISSION_RATE_STOCK_US: float = float(os.getenv("COMMISSION_RATE_STOCK_US"))
    # 증권 거래세
    TAX_RATE_STOCK_KR: float = float(os.getenv("TAX_RATE_STOCK_KR"))
    # 해외 수수료
    INTERNATIONAL_TRANSACTION_FEES: float = float(os.getenv("INTERNATIONAL_TRANSACTION_FEES"))
    # 배당 소득세
    DIVIDEND_TAX_RATE_STOCK_KR: float = float(os.getenv("DIVIDEND_TAX_RATE_STOCK_KR"))
    DIVIDEND_TAX_RATE_STOCK_US: float = float(os.getenv("DIVIDEND_TAX_RATE_STOCK_US"))
    
    
    # 기본 계정과목 데이터
    BASE_ACCOUNTS = {
        "common": {
            "assets": [
            {"code": "1001", "name": "현금및예금", "type": "유동자산", "account_metadata": {"description": "일반 현금 및 예금"}},
            {"code": "1002", "name": "외화예금", "type": "유동자산", "account_metadata": {"description": "외화 예금"}},
            {"code": "1003", "name": "투자예치금", "type": "유동자산", "account_metadata": {"description": "투자를 위한 예치금"}}
        ],
        "liabilities": [
            {"code": "2001", "name": "신용융자금", "type": "유동부채", "account_metadata": {"description": "신용거래 융자금"}},
            {"code": "2002", "name": "미지급금", "type": "유동부채", "account_metadata": {"description": "미지급 금액"}},
            {"code": "2003", "name": "차입금", "type": "유동부채", "account_metadata": {"description": "외부 차입금"}}
        ],
        "equity": [
            {"code": "3001", "name": "원본", "type": "자본금", "account_metadata": {"description": "투자 원본"}},
            {"code": "3002", "name": "이익잉여금", "type": "잉여금", "account_metadata": {"description": "누적 이익금"}}
        ],
        "expenses": [
            {"code": "4001", "name": "이자비용", "type": "금융비용", "account_metadata": {"description": "차입금 이자"}},
            {"code": "4002", "name": "환차손", "type": "금융비용", "account_metadata": {"description": "환율 변동 손실"}},
            {"code": "4003", "name": "수수료비용", "type": "영업비용", "account_metadata": {"description": "일반 수수료"}}
        ],
        "income": [
            {"code": "5001", "name": "이자수익", "type": "금융수익", "account_metadata": {"description": "예금 이자"}},
            {"code": "5002", "name": "환차익", "type": "금융수익", "account_metadata": {"description": "환율 변동 이익"}}
        ]
        },
        "stocks": {
            "assets": [
                {"code": "1101", "name": "국내주식", "type": "투자자산", "account_metadata": {"description": "국내 주식 투자"}},
                {"code": "1102", "name": "해외주식", "type": "투자자산", "account_metadata": {"description": "해외 주식 투자"}},
                {"code": "1103", "name": "미수금", "type": "당좌자산", "account_metadata": {"description": "주식 거래 미수금"}},
                {"code": "1104", "name": "미수배당금", "type": "당좌자산", "account_metadata": {"description": "주식 배당 미수금"}}
            ],
            "expenses": [
                {"code": "4101", "name": "주식매매수수료", "type": "거래비용", "account_metadata": {"description": "주식 거래 수수료"}},
                {"code": "4102", "name": "증권거래세", "type": "세금", "account_metadata": {"description": "주식 거래세"}},
                {"code": "4103", "name": "매매차손", "type": "매매손실", "account_metadata": {"description": "주식 매매 손실"}},
                {"code": "4104", "name": "평가손실", "type": "평가손실", "account_metadata": {"description": "주식 평가 손실"}},
                {"code": "4105", "name": "양도세", "type": "세금", "account_metadata": {"description": "양도세"}},
                {"code": "4106", "name": "인지세", "type": "세금", "account_metadata": {"description": "국외제비용"}}
            ],
            "income": [
                {"code": "5101", "name": "매매차익", "type": "매매이익", "account_metadata": {"description": "주식 매매 이익"}},
                {"code": "5102", "name": "평가이익", "type": "평가이익", "account_metadata": {"description": "주식 평가 이익"}},
                {"code": "5103", "name": "배당금수익", "type": "배당수익", "account_metadata": {"description": "주식 배당금"}}
            ]
        },
        "crypto": {
            "assets": [
                {"code": "1201", "name": "암호화폐", "type": "투자자산", "account_metadata": {"description": "암호화폐 보유분"}},
                {"code": "1202", "name": "거래소예치금", "type": "유동자산", "account_metadata": {"description": "거래소 예치금"}},
                {"code": "1203", "name": "지갑보유분", "type": "투자자산", "account_metadata": {"description": "개인 지갑 보유분"}}
            ],
            "expenses": [
                {"code": "4201", "name": "거래수수료", "type": "거래비용", "account_metadata": {"description": "암호화폐 거래 수수료"}},
                {"code": "4202", "name": "송금수수료", "type": "거래비용", "account_metadata": {"description": "암호화폐 송금 수수료"}},
                {"code": "4203", "name": "매매차손", "type": "매매손실", "account_metadata": {"description": "암호화폐 매매 손실"}},
                {"code": "4204", "name": "평가손실", "type": "평가손실", "account_metadata": {"description": "암호화폐 평가 손실"}}
            ],
            "income": [
                {"code": "5201", "name": "매매차익", "type": "매매이익", "account_metadata": {"description": "암호화폐 매매 이익"}},
                {"code": "5202", "name": "평가이익", "type": "평가이익", "account_metadata": {"description": "암호화폐 평가 이익"}},
                {"code": "5203", "name": "채굴수익", "type": "채굴수익", "account_metadata": {"description": "암호화폐 채굴 수익"}},
                {"code": "5204", "name": "스테이킹수익", "type": "이자수익", "account_metadata": {"description": "암호화폐 스테이킹 수익"}}
            ]
        }
    }
# 설정 인스턴스 생성    
settings = Settings()
