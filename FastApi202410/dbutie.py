import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import json
from datetime import datetime

# 현재 실행 파일의 경로에서 데이터베이스 파일 경로 생성
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, "K202410.db")
DATABASE_URL = f"sqlite:///{db_path}"

# Manga 모델 정의
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, Float

Base = declarative_base()

class Manga(Base):
    __tablename__ = "manga"
    
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    folder_name = Column(Text, unique=True, index=True, nullable=False)
    tags = Column(Text, nullable=True)
    page = Column(Integer)
    images_name = Column(Text, nullable=True)
    create_date = Column(DateTime, nullable=True, default=datetime.now())
    update_date = Column(DateTime, nullable=True, default=datetime.now())
    file_date = Column(DateTime, nullable=True)
    
    rating_sum = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    rating_average = Column(Float, default=0.0)
    view_count = Column(Integer, default=0)

def cleanup_manga_images():
    # 데이터베이스 연결
    print(f"데이터베이스 경로: {db_path}")
    engine = create_engine(DATABASE_URL)
    
    with Session(engine) as db:
        try:
            # 모든 망가 레코드 조회
            mangas = db.query(Manga).all()
            update_count = 0
            
            print(f"총 {len(mangas)}개의 레코드를 처리합니다...")
            
            for manga in mangas:
                try:
                    # JSON 문자열을 파이썬 리스트로 변환
                    if manga.images_name:
                        images = json.loads(manga.images_name)
                        
                        # 이미지 이름 정리
                        cleaned_images = []
                        for img in images:
                            # 파일명만 추출
                            file_name = os.path.basename(img)
                            cleaned_images.append(file_name)
                        
                        # 변경사항이 있는 경우에만 업데이트
                        if images != cleaned_images:
                            manga.images_name = json.dumps(cleaned_images)
                            update_count += 1
                            
                            print(f"\n처리됨 ({manga.id}): {manga.folder_name}")
                            print(f"  이전: {images[:2]}")
                            print(f"  이후: {cleaned_images[:2]}")
                
                except json.JSONDecodeError:
                    print(f"\nJSON 파싱 에러 (manga_id: {manga.id}): {manga.images_name[:100]}...")
                    continue
                except Exception as e:
                    print(f"\n처리 중 에러 발생 (manga_id: {manga.id}): {str(e)}")
                    continue
            
            # 변경사항 저장
            db.commit()
            print(f"\n처리 완료: {update_count}개의 레코드가 업데이트되었습니다.")
            
        except Exception as e:
            print(f"데이터베이스 처리 중 에러 발생: {str(e)}")
            db.rollback()

def verify_manga_images():
    """변경된 데이터 확인"""
    engine = create_engine(DATABASE_URL)
    
    with Session(engine) as db:
        mangas = db.query(Manga).all()
        issues_found = 0
        
        print("\n데이터 검증 시작...")
        
        for manga in mangas:
            try:
                if manga.images_name:
                    images = json.loads(manga.images_name)
                    
                    # 경로가 포함된 이미지가 있는지 확인
                    has_path = any('/' in img for img in images)
                    
                    if has_path:
                        issues_found += 1
                        print(f"\n경로가 남아있는 레코드 발견 (manga_id: {manga.id}):")
                        print(f"  폴더명: {manga.folder_name}")
                        print(f"  이미지 예시: {images[:2]}")
            
            except json.JSONDecodeError:
                issues_found += 1
                print(f"\nJSON 파싱 에러 (manga_id: {manga.id})")
                continue
        
        if issues_found == 0:
            print("모든 레코드가 정상적으로 처리되었습니다.")
        else:
            print(f"\n총 {issues_found}개의 문제가 발견되었습니다.")

if __name__ == "__main__":
    print("이미지 경로 정리 프로그램")
    print("=" * 50)
    print(f"데이터베이스: {db_path}")
    print("=" * 50)
    
    if not os.path.exists(db_path):
        print("오류: 데이터베이스 파일을 찾을 수 없습니다!")
        exit(1)
        
    response = input("이미지 이름을 정리하시겠습니까? (y/n): ").lower()
    if response == 'y':
        cleanup_manga_images()
        verify_manga_images()
    else:
        print("\n작업이 취소되었습니다.")