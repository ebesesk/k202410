from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import json
import os
from app.models.manga import Manga
from app.core.config import settings

def cleanup_manga_images():
    # 데이터베이스 연결
    engine = create_engine('sqlite:///K202410.db')
    
    with Session(engine) as db:
        try:
            # 모든 망가 레코드 조회
            mangas = db.query(Manga).all()
            
            for manga in mangas:
                try:
                    # JSON 문자열을 파이썬 리스트로 변환
                    if manga.images_name:
                        images = json.loads(manga.images_name)
                        
                        # 폴더명 추출 (경로에서 마지막 부분)
                        folder_name = manga.folder_name.split('/')[-1]
                        
                        # 이미지 이름 정리
                        cleaned_images = []
                        for img in images:
                            # 파일명만 추출
                            file_name = os.path.basename(img)
                            cleaned_images.append(file_name)
                        
                        # 정리된 이미지 리스트를 JSON 문자열로 변환하여 저장
                        manga.images_name = json.dumps(cleaned_images)
                        
                        print(f"처리됨: {manga.folder_name}")
                        print(f"  이전: {images[:2]}...")
                        print(f"  이후: {cleaned_images[:2]}...")
                        print("-------------------")
                
                except json.JSONDecodeError:
                    print(f"JSON 파싱 에러 (manga_id: {manga.id}): {manga.images_name}")
                    continue
                except Exception as e:
                    print(f"처리 중 에러 발생 (manga_id: {manga.id}): {str(e)}")
                    continue
            
            # 변경사항 저장
            db.commit()
            print("모든 처리가 완료되었습니다.")
            
        except Exception as e:
            print(f"데이터베이스 처리 중 에러 발생: {str(e)}")
            db.rollback()

def verify_manga_images():
    """변경된 데이터 확인"""
    engine = create_engine('sqlite:///K202410.db')
    
    with Session(engine) as db:
        mangas = db.query(Manga).all()
        
        for manga in mangas:
            try:
                if manga.images_name:
                    images = json.loads(manga.images_name)
                    
                    # 경로가 포함된 이미지가 있는지 확인
                    has_path = any('/' in img for img in images)
                    
                    if has_path:
                        print(f"경로가 남아있는 레코드 발견 (manga_id: {manga.id}):")
                        print(f"  폴더명: {manga.folder_name}")
                        print(f"  이미지 예시: {images[:2]}")
                        print("-------------------")
            
            except json.JSONDecodeError:
                print(f"JSON 파싱 에러 (manga_id: {manga.id})")
                continue

if __name__ == "__main__":
    # 사용자 확인
    response = input("이미지 이름을 정리하시겠습니까? (y/n): ").lower()
    if response == 'y':
        cleanup_manga_images()
        print("\n데이터 확인 중...")
        verify_manga_images()
    else:
        print("작업이 취소되었습니다.")