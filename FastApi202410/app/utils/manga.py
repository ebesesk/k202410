from pathlib import Path
import os
# from app.models.manga import Manga
from datetime import datetime
from sqlalchemy.orm import Session
# from app.models.manga import Manga
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import pytz  # 한국 시간대를 설정하기 위한 라이브러리

# 한국 시간대 설정
KST = pytz.timezone("Asia/Seoul")

def list_images_from_folders(base_folder_path: str) -> List[Dict]:
    
    manga_entries = []
    for folder in Path(base_folder_path).iterdir():
        if folder.is_dir() and not(folder.name.startswith("__")) and ('@eaDir' not in folder.name):
            folder_name = folder.name
            images = list(folder.glob("*.*"))  # 모든 파일 검색
            images = [img for img in images if '@eaDir' not in img.name]
            # 이미지 파일 수가 페이지 수로 사용될 수 있습니다
            page_count = len(images)
            images_name = ", ".join([img.name for img in images])
            create_date = datetime.now()

            # 파일의 최신 수정 날짜를 `file_date`로 설정
            file_date = min(img.stat().st_mtime for img in images)
            file_date = datetime.fromtimestamp(file_date)

            manga_entries.append({
                        "folder_name": folder_name,
                        "tags": "",
                        "page": page_count,
                        "images_name": images_name,
                        "create_date": create_date,
                        "update_date": create_date,
                        "file_date": file_date
                    })
    
    
    special_folder_entries = []

    # 상위 폴더를 스캔하여 "__"로 시작하는 폴더만 처리
    for main_folder in Path(base_folder_path).iterdir():
        if main_folder.is_dir() and main_folder.name.startswith("__") and ('@eaDir' not in folder.name):
            # 상위 폴더의 각 하위 폴더를 스캔
            for sub_folder in main_folder.rglob('*'):
                if sub_folder.is_dir():
                    folder_name = f"{main_folder.name}/{sub_folder.name}"
                    
                    # 하위 폴더의 이미지 파일 수집
                    images = list(sub_folder.glob("*.*"))
                    images = [img for img in images if '@eaDir' not in img.name]
                    page_count = len(images)
                    images_name = ", ".join([img.name for img in images])
                    
                    # KST로 시간 설정
                    create_date = datetime.now(KST)
                    file_date = min(img.stat().st_mtime for img in images) if images else None
                    file_date = datetime.fromtimestamp(file_date, tz=pytz.utc).astimezone(KST) if file_date else None

                    if '@eaDir' not in folder_name:
                        # 각 하위 폴더의 이미지 정보 추가
                        special_folder_entries.append({
                            "folder_name": folder_name,
                            "page": page_count,
                            "images_name": images_name,
                            "create_date": create_date,
                            "update_date": create_date,
                            "file_date": file_date
                        })
    manga_entries = manga_entries + special_folder_entries
    return manga_entries


if __name__ == "__main__":
    list_images_from_folders('/home/manga')
    for j,i in enumerate(list_images_from_folders('/home/manga')):
        if isinstance(i['page'], int) and isinstance(i['create_date'], datetime) and isinstance(i['file_date'], datetime) and isinstance(i['update_date'], datetime) and isinstance(i['images_name'], str) and isinstance(i['folder_name'], str):
            if '@eaDir' in i['folder_name'] or '@eaDir' in i['images_name']:
                print(j, i['folder_name'], i['page'], i['file_date'])
            pass
        else:
            print(j, i['folder_name'], i['page'], i['file_date'])
            print('===================================================')