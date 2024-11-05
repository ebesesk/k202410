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
import json
import re, glob, shutil
from math import ceil
# 한국 시간대 설정
KST = pytz.timezone("Asia/Seoul")
img_extensions = ['jpg', 'png', 'jpeg', 'gif', 'bmp', 'tiff', 'webp', 'zip', 'rar', '7z', 'tar', '.gz', 'bz2', 'xz', 'alz']
zip_extensions = ['zip', 'rar', '7z', 'tar', '.gz', 'bz2', 'xz', 'alz']
MANGA_PATH = '/home/manga'


def remove_repeat_regex(s):
    pattern = r'(.+?)\1+'
    match = re.match(pattern, s)
    return match.group(1) if match else s

def del_specialCharacter(text):
    text = text.strip()
    patterns = [
        r'[|\\{}]',          # 파이프와 중괄호
        r'[\[\]/?]',         # 대괄호와 슬래시
        r'[.,;:!]',          # 구두점
        r'[*~`^]',          # 특수 기호
        r'[+<>@#$%&=]',     # 연산자와 특수 문자
        r'[\(\)\'\"]',      # 괄호와 따옴표
        r'[-_]',            # 하이픈과 언더스코어
        r'\s+',             # 공백
        r'_+',              # 언더스코어
    ]   
    for pattern in patterns:
        text = re.sub(pattern, ' ', text)
    text = text.strip().replace(' ', '_')
    return text

def rename_file(old_name, new_name):
    if old_name != new_name:
        old_file = old_name
        new_file = new_name
        for old_file, new_file in zip(old_name, new_name):

            if old_file != new_file and new_file and not os.path.isdir(new_file):
                # print('old_file:', old_file)
                # print('new_file:', new_file)
                print('=========================================')
                try:    
                    os.rename(old_file, new_file)
                    print('copy:', old_file,'\n'
                          'to  :', new_file)
                except Exception as e:
                    pass
                    print('e:', e)
                    print('old_file:', old_file)
        
                

def rename_images_name(folder_name, images_name):
    if len(images_name) == 0:
        return False, False
    # 폴더 경로 추출
    header = images_name[0][:images_name[0].rfind('/')]
    title = folder_name[folder_name.rfind('/')+1:]
    zfill_count = len(str(len(images_name)))
 
    new_file_names = []
    for i, img_name in enumerate(images_name):


        _ext = img_name[-4:].replace('.', '').replace('_', '')
        if _ext.lower() not in img_extensions:
            new_file_names.append(False)
    
        elif os.path.isdir(img_name):
            new_file_names.append(False)

        elif 'Thumbs_db' in img_name:
            new_file_names.append(False)
        
        elif '.'+_ext.lower() in img_name.lower():
            new_file_names.append(False)
        
        elif 'svg%3E' in img_name:
            new_file_names.append(False)
        

        elif _ext.lower() in img_extensions:
            new_file_name = img_name[:-5] + img_name[-5:].replace('_' + _ext, '.' + _ext)
            header = new_file_name[:new_file_name.rfind('/')]
            title = new_file_name[new_file_name.rfind('/')+1:new_file_name.rfind('.')]
            title = del_specialCharacter(title)
            new_file_name = header + '/' + title + '.' + _ext
            if new_file_name not in new_file_names and new_file_name != img_name:
                new_file_names.append(new_file_name)
        else:
            new_file_names.append(False)

        
    return images_name, new_file_names
        




def list_images_from_folders(MANGA_PATH: str) -> List[Dict]:
    '''
    이미지 파일 목록 추출 및 이미지 파일 이름 변경
    출력 예시
    {
        'folder_name': '장르/만화명',
        'tags': '',
        'images_name': ['이미지 파일 경로 리스트'],
        'file_date': '이미지 파일 생성일자'
    }   
    '''
    manga_folders = []
    for genres_folder in os.listdir(MANGA_PATH):
        for manga_folder in os.listdir(os.path.join(MANGA_PATH, genres_folder)):
            manga_folder_path = os.path.join(MANGA_PATH, genres_folder, manga_folder)
            manga_images = glob.glob(manga_folder_path+'/*')
            if os.path.isdir(manga_folder_path) and len(manga_images) > 0:
                manga_folders.append(manga_folder_path)
            if len(manga_images) == 0:  # 빈 만화 폴더 출력
                print('빈 만화:', manga_folder_path)
                remove_folder(manga_folder_path)
                
    manga_list = []
    for manga_folder in manga_folders:
        folder_name = manga_folder.replace(MANGA_PATH + '/', '')
        file_date = datetime.now(KST)
        images_name = []
        tags = {'size': 0}
        for img in glob.glob(manga_folder+'/*'):
            if '@eaDir' not in img \
                and 'svg%3E' not in img \
                    and os.path.isfile(img) \
                        and img[img.rfind('.')+1:].lower() in img_extensions:    
                images_name.append(os.path.basename(img))
                if img[img.rfind('.')+1:].lower() in zip_extensions:
                    size = float(os.path.getsize(img)) / 1024 / 1024
                    tags['size'] += size
                    # print(img, size)
                file_stat = os.stat(img)
                file_date_new = datetime.fromtimestamp(file_stat.st_mtime, KST)
                if file_date_new < file_date:
                    file_date = file_date_new
        tags['size'] = str(int(ceil(tags['size']))) + 'MB'
        manga_dict = {
            'folder_name': folder_name,
            'tags': tags,
            'images_name': images_name,
            'file_date': file_date,
            'page': len(images_name),
            # 'update_date': datetime.now(KST)
        }
        manga_list.append(manga_dict)

        # rename_images_name(folder_name, images_name[:50])    
    print("list_images_from_folders:", len(manga_list))
    return manga_list

def get_genres_list():
    genres_list = [i for i in os.listdir(MANGA_PATH) if os.path.isdir(os.path.join(MANGA_PATH, i))]
    return genres_list


def rename_images_name(folder_name, images_name):
    if len(images_name) == 0:
        return False
    
    images_name.sort()
    
    for i, img_name in enumerate(images_name):
        img_path = os.path.join(MANGA_PATH, folder_name, img_name)
        if os.path.isfile(img_path):
            img_path_new = os.path.join(MANGA_PATH, folder_name, str(i).zfill(zfill_count) + '.' + img_path.split('.')[-1])
            print('img_path:', img_path)
            print('=========================================')

def rename_folder(old_path: str, new_name: str) -> bool:
    """
    폴더 이름을 변경합니다.
    
    Args:
        old_path: 현재 폴더 경로
        new_name: 새로운 폴더 이름
    
    Returns:
        bool: 성공 여부
    """
    try:
        # 상위 디렉토리 경로 가져오기
        parent_dir = os.path.dirname(old_path)
        # 새로운 전체 경로 생성
        new_path = os.path.join(parent_dir, new_name)
        
        # 이미 같은 이름의 폴더가 있는지 확인
        if os.path.exists(new_path):
            print(f"이미 존재하는 폴더명입니다: {new_name}")
            return False
            
        # 폴더 이름 변경
        os.rename(old_path, new_path)
        print(f"폴더명 변경 성공: {old_path} -> {new_path}")
        return True
        
    except Exception as e:
        print(f"폴더명 변경 실패: {str(e)}")
        return False          
     
def remove_file(file_path: str) -> bool:
    """
    단일 파일을 삭제합니다.
    """
    try:
        os.remove(file_path)  # 또는 Path(file_path).unlink()
        print(f"파일 삭제 완료: {file_path}")
        return True
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return False
    except Exception as e:
        print(f"파일 삭제 실패: {str(e)}")
        return False

def remove_folder(folder_path: str, recursive: bool = True) -> bool:
    """
    폴더를 삭제합니다.
    recursive=True: 폴더 내 모든 내용 삭제
    recursive=False: 빈 폴더만 삭제
    """
    try:
        if recursive:
            shutil.rmtree(folder_path)  # 폴더와 내용 모두 삭제
        else:
            os.rmdir(folder_path)  # 빈 폴더만 삭제
        print(f"폴더 삭제 완료: {folder_path}")
        return True
    except FileNotFoundError:
        print(f"폴더를 찾을 수 없습니다: {folder_path}")
        return False
    except Exception as e:
        print(f"폴더 삭제 실패: {str(e)}")
        return False

# 여러 파일 일괄 삭제
def batch_remove(directory: str, pattern: str = "*", recursive: bool = False) -> dict:
    """
    디렉토리 내의 특정 패턴의 파일들을 삭제합니다.
    """
    stats = {"success": 0, "failed": 0, "skipped": 0}
    
    try:
        path = Path(directory)
        # 파일 검색
        if recursive:
            files = list(path.rglob(pattern))  # 하위 디렉토리 포함
        else:
            files = list(path.glob(pattern))   # 현재 디렉토리만
        
        if not files:
            print(f"삭제할 파일을 찾을 수 없습니다: {pattern}")
            return stats
        
        # 삭제 확인
        print(f"총 {len(files)}개의 파일이 검색되었습니다.")
        for file in files:
            print(f"- {file}")
        
        response = input("이 파일들을 삭제하시겠습니까? (y/n): ").lower()
        if response != 'y':
            print("삭제가 취소되었습니다.")
            stats["skipped"] = len(files)
            return stats
        
        # 파일 삭제
        for file in files:
            try:
                if file.is_file():
                    file.unlink()
                else:
                    shutil.rmtree(file)
                stats["success"] += 1
                print(f"삭제됨: {file}")
            except Exception as e:
                stats["failed"] += 1
                print(f"삭제 실패 ({file}): {str(e)}")
        
        return stats
        
    except Exception as e:
        print(f"일괄 삭제 중 오류 발생: {str(e)}")
        return stats



if __name__ == "__main__":
    list_images_from_folders('/home/manga')
    # for j,i in enumerate(list_images_from_folders('/home/manga')):
    #     if isinstance(i['page'], int) and isinstance(i['create_date'], datetime) and isinstance(i['file_date'], datetime) and isinstance(i['update_date'], datetime) and isinstance(i['images_name'], str) and isinstance(i['folder_name'], str):
    #         if '@eaDir' in i['folder_name'] or '@eaDir' in i['images_name']:
    #             print(j, i['folder_name'], i['page'], i['file_date'])
    #         pass
    #     else:
    #         print(j, i['folder_name'], i['page'], i['file_date'])
    #         print('===================================================')