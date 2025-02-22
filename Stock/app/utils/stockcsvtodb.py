import csv
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from decimal import Decimal
from app.models.stock import Transaction, Base  # 모델이 정의된 모듈을 import

# # 데이터베이스 연결 설정
# DATABASE_URL = "sqlite:///./test.db"  # 예시로 SQLite 사용
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # 데이터베이스 테이블 생성
# Base.metadata.create_all(bind=engine)

def load_csv_to_db(file_path: str, db: Session):
    # 데이터베이스 세션 생성
    # db: Session = SessionLocal()

    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # 헤더 건너뛰기

            for row in reader:
                # CSV 파일의 각 열을 모델의 필드에 매핑
                transaction = Transaction(
                    date=datetime.strptime(row[0], "%Y/%m/%d").date(),
                    asset_category=row[1],
                    currency=row[11],  # 종목명
                    amount=Decimal(row[3].replace(',', '')),
                    action=row[1],  # 거래종류
                    interest=Decimal(row[15].replace(',', '')) if row[15] else None,
                    fee=Decimal(row[4].replace(',', '')) if row[4] else Decimal('0.00'),
                    tax=Decimal(row[14].replace(',', '')) if row[14] else Decimal('0.00'),
                    username="default_user",  # 사용자 이름을 적절히 설정
                    memo=row[12]  # 거래단가
                )
                db.add(transaction)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

# CSV 파일 경로
csv_file_path = "/home/kds/k202410/Stock/app/utils/trade.csv"
load_csv_to_db(csv_file_path)