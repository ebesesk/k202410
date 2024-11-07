from pathlib import Path
import os
# from app.models.manga import Manga
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.manga import Manga
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Union, Tuple
import pytz  # 한국 시간대를 설정하기 위한 라이브러리
import json
import re, glob, shutil
from math import ceil
from app.models.manga import Manga
from app.core.config import settings
from app.utils.utils import get_unique_path, del_specialCharacter, move_folder, get_unique_path, get_max_file_number_length

# 상수 정의
# # 한국 시간대 설정
KST = pytz.timezone("Asia/Seoul")
IMG_EXT = ['jpg', 'png', 'jpeg', 'gif', 'bmp', 'tiff', 'webp', 'zip', 'rar', '7z', 'tar', '.gz', 'bz2', 'xz', 'alz']
ZIP_EXT = ['zip', 'rar', '7z', 'tar', '.gz', 'bz2', 'xz', 'alz']
BASE_PATH = settings.IMAGE_DIRECTORY
FOLDER_NAME_PREFIX_LENGTH = 2
FILE_NAME_SEPARATOR = '_'


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

def get_manga_info(folder_name: str) -> Dict:
    """
    망가 폴더 정보를 추출합니다.
    """
    if BASE_PATH in folder_name:
        folder_name = folder_name.replace(BASE_PATH + os.path.sep, '')
    manga_path = os.path.join(BASE_PATH, folder_name)
    
    tags = {'size': 0}
    images_name = []
    file_date = datetime.now(KST)
    # page = 0

    for img in glob.glob(manga_path+'/*'):
        if os.path.isfile(img) and get_extension(img) in IMG_EXT + ZIP_EXT:
            images_name.append(os.path.basename(img))
            if get_extension(img) in ZIP_EXT:
                size = float(os.path.getsize(img)) / 1024 / 1024
                tags['size'] += size
            file_stat = os.stat(img)
            file_date_new = datetime.fromtimestamp(file_stat.st_mtime, KST)
            if file_date_new < file_date:
                file_date = file_date_new
            # page += 1
    
    return {
        'folder_name': folder_name,
        'tags': json.dumps(tags),
        'images_name': json.dumps(images_name),
        'file_date': file_date,
        'page': len(images_name)
    }

def get_extension(file_path: str) -> str:
    return file_path[file_path.rfind('.')+1:].lower()

def create_result_dict(manga: Manga, msg: str, success: bool, images_name: List[str] = [], tags: Dict = {}) -> Dict:
    """
    결과 딕셔너리를 생성합니다.
    
    Args:
        manga: 망가 객체
        msg: 결과 메시지
        success: 성공 여부
        images_name: 이미지 파일 목록 (선택적 인자)
        tags: 태그 딕셔너리 (선택적 인자)   
    
    Returns:
        Dict: 결과 딕셔너리
    """
    return {
        'manga': manga,
        'msg': msg,
        'success': success,
        'images_name': images_name,
        'tags': tags
    }

def get_relative_path(full_path: str) -> str:
    """
    전체 경로에서 상대 경로를 추출합니다.
    
    Args:
        full_path: 전체 경로
        
    Returns:
        str: 상대 경로
    """
    return full_path.replace(settings.IMAGE_DIRECTORY + os.path.sep, '')

def generate_new_filename(index: int, original_filename: str) -> str:
    """
    새로운 파일명을 생성합니다.
    
    Args:
        index: 파일 인덱스
        original_filename: 원본 파일명
    
    Returns:
        str: 새로운 파일명
    """
    filename, ext = os.path.splitext(original_filename)
    return f"{str(index+1).zfill(FOLDER_NAME_PREFIX_LENGTH)}{FILE_NAME_SEPARATOR}{filename}{ext}"

def get_genres_list():
    genres_list = [i for i in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, i))]
    return genres_list


def list_images_from_folders() -> List[Dict]:
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
    manga_list = []
    manga_folders = []
    genre_folders = [os.path.join(BASE_PATH, genre) for genre in get_genres_list()]
    for genre in genre_folders:           
        _dir = os.listdir(genre)
        if os.path.isdir(genre):
            manga_folders.extend([os.path.join(genre, manga) for manga in _dir])
    
    for manga_folder in manga_folders:
        manga_info = get_manga_info(manga_folder)
        manga_list.append(manga_info)
        # get_manga_info 함수에서 반환된 딕셔너리를 사용하여 Manga 객체 생성
        # manga_info = {
        #     'folder_name': manga_folder,
        #     'tags': manga_info['tags'],
        #     'images_name': manga_info['images_name'],
        #     'file_date': manga_info['file_date'],
        #     'page': manga_info['page']
        # }
        # manga = Manga(**manga_info)
        # manga_list.append(manga)

    print("list_images_from_folders:", len(manga_list))
    return manga_list


def move_manga_folder(mangas: List[Manga], target_folder_name: str) -> List[Dict]:
    """
    망가 폴더들을 대상 폴더로 이동합니다.
    
    Args:
        mangas: 이동할 망가 모델 리스트
        target_folder_name: 대상 폴더명
        
    Returns:
        List[Dict]: 이동 결과 목록
    """
    result = []
    
    for manga in mangas:
        source_path = os.path.join(BASE_PATH, manga.folder_name)
        target_path = get_unique_path(os.path.join(BASE_PATH, target_folder_name))
        
        success, msg = move_folder(source_path, target_path)
        
        if success:
            manga_info = get_manga_info(target_path)
            manga.folder_name = manga_info['folder_name']
            manga.tags = manga_info['tags']
            manga.images_name = manga_info['images_name']
            manga.file_date = manga_info['file_date']
            manga.page = manga_info['page']
            manga.update_date = datetime.now(KST)
        
        result.append(create_result_dict(manga, msg, success))
    
    return result


def merge_manga_folder(mangas: List[Manga], target_folder_name: str) -> List[Dict]:
    """
    여러 망가 폴더를 하나의 대상 폴더로 병합합니다.
    target_folder_name이 기존 manga의 folder_name과 동일한 경우 해당 폴더를 사용합니다.

    Args:
        mangas: 병합할 망가 모델 리스트
        target_folder_name: 병합 대상 폴더 이름
        
    Returns:
        List[Dict]: 병합 결과 목록
    """
    
    
    def get_volumes_number(BASE_PATH: str, folder_name: str) -> List[str]:
        """
        망가 폴더 내 볼륨 번호 목록을 반환합니다.
        volume|number
        volume: 볼륨 번호 2자리수
        number: 같은 볼륨 있을경우 번호 증가 1자리수
        """
        volumes_number = []
        zfill_count = 0
        if BASE_PATH in folder_name:
            folder_name = folder_name.replace(BASE_PATH + os.path.sep, '')
        manga_path = BASE_PATH + os.path.sep + os.path.dirname(folder_name)
        for file in os.listdir(manga_path):
            if os.path.isfile(os.path.join(manga_path, file)) and get_extension(file) in IMG_EXT + ZIP_EXT:
                basename = os.path.basename(file)
                name, ext = os.path.splitext(basename)
                volume_number = re.findall(r'_([\d]+)-', name)  # 볼륨 선택
                if volume_number:
                    volumes_number.append(volume_number[0])
                    zfill_count = max(zfill_count, len(volume_number[0]))
        volumes_number.sort()
        return list(set(volumes_number)), zfill_count
    
    def get_volumes_number_db(manga: Manga) -> Tuple[str, List[str], int, int]:
        """
        망가 모델에서 볼륨 번호 목록을 반환합니다.
        (volume+number)   _010-001 _011-001 _010-002
        volume: 볼륨 번호 2자리수 이상 000 초기값
        number: 같은 볼륨 있을경우 번호 증가 1자리수 0 초기값
        page: 페이지 번호 3자리수 이상 000 초기값
        """
        volumes = []
        volume_zfill_count = 0
        page_zfill_count = 0
      
        for image in json.loads(manga.images_name):
            name, ext = os.path.splitext(image)
            page = re.findall(r'-?\d+$', name)   
            page_zfill_count = max(page_zfill_count, len(page[0]))
            volume = re.findall(r'_?(\d+)-', name)
            if volume:
                volumes.append(volume[0]) if volume[0] not in volumes else None
                volume_zfill_count = max(volume_zfill_count, len(volume[0][:-2]))
        volumes.sort()
        return volumes, volume_zfill_count, page_zfill_count
            
    
    
    
    def get_max_page_number_length(mangas: List[Manga]) -> int:
        """
        파일 목록에서 숫자로 시작하는 가장 긴 숫자의 길이를 반환합니다.
    
        Args:
            BASE_PATH: 기본 경로
            folder_name: 폴더명
            
        Returns:
            int: 가장 긴 숫자의 길이
        """
        max_page_number_length = 0
        for manga in mangas:
            for img in json.loads(manga.images_name):   
                page = re.findall(r'-?\d+$', img)
                if page:
                    max_page = max([len(page[0])])
                    max_page_number_length = max(max_page_number_length, max_page)
        return max_page_number_length   

    def get_unique_volume(volume: str, volumes: List[str], volume_zfill: int = 2) -> str:
        """
        중복되지 않는 볼륨 번호를 찾아서 반환합니다.
        volume: 파일명 마지막 vol숫자 vol01 vol1 등
        """
        print('volume:', volume)
        print('volumes:', volumes)
        if volume not in volumes:
            return volume
        counter = 1
        while True:
            new_volume = f"{volume[:-1].zfill(volume_zfill)}{str(counter)}"
            if new_volume not in volumes:
                return new_volume
            counter += 1
    
    VOLUME_ZFILL_COUNT = 2    
    PAGE_ZFILL_COUNT = 3
    VOLUME_SEPARATOR = '-'
    dest_path = os.path.join(BASE_PATH, target_folder_name)
    srcs_path = [os.path.join(BASE_PATH, manga.folder_name) for manga in mangas]
    
    if dest_path not in srcs_path:
        ...
        ########################################################################################################
        # os.makedirs(get_unique_path(os.path.join(dest_path)))    # 병합 시 중복 폴더 생성 방지 
        ########################################################################################################

    volumes, volume_zfill, page_zfill = get_volumes_number_db(mangas[0])
    if not volumes:
        volumes = ['000']
    if not volume_zfill:
        volume_zfill = VOLUME_ZFILL_COUNT
    if page_zfill < PAGE_ZFILL_COUNT:
        page_zfill = PAGE_ZFILL_COUNT
        
    max_zfill = get_max_page_number_length(mangas)
    
    def get_volume(manga: Manga, name: str, volume_zfill: int, volumes: List[str]) -> str:
        
        if re.findall(r'_?(\d+)-', name):
            volume = re.findall(r'_?(\d+)-', name)[0]
            volume = f"{volume.zfill(volume_zfill)}0"
            print('volume1:', volume)
        elif re.findall(r'[vV][oO][lL][_]?(\d+)$' , manga.folder_name): 
            volume = re.findall(r'[vV][oO][lL][_]?(\d+)$', manga.folder_name)[0]
            volume = f"{volume.zfill(volume_zfill)}0"
            print('volume2:', volume)
        else:
            volume = int(volumes[-1][:-1]) + 1
            volume = f"{str(volume).zfill(volume_zfill)}0"
            print('volume3:', volume)
        # volume = get_unique_volume(volume, volumes, volume_zfill)
        # volumes.append(volume) if volume not in volumes else None
        return volume, volumes
    
    images_name = []
    tags = {}
    tags['titles'] = ''        
    folder_name = ''
    for manga, src_path in zip(mangas, srcs_path):
        volume = ''
        for img in json.loads(manga.images_name):
            name, ext = os.path.splitext(img)
            # 정규식 패턴 개선
            volume1 = re.search(r'(\d+)-', name)  # 파일명에서 숫자- 패턴 찾기
            volume2 = re.search(r'[Vv][Oo][Ll][UuMmEe]{0,3}[_]?(\d+)$', manga.folder_name)  # 폴더명에서 vol숫자 패턴 찾기
            
            if (volume1 or volume2) and folder_name != manga.folder_name:
                # 볼륨 번호가 있고 새로운 폴더일 때
                volume, volumes = get_volume(manga, img, volume_zfill, volumes)
            elif not (volume1 or volume2):
                # 볼륨 번호가 없을 때
                volume, volumes = get_volume(manga, img, volume_zfill, volumes)
                
            if folder_name != manga.folder_name:
                volume = get_unique_volume(volume, volumes, volume_zfill)
                folder_name = manga.folder_name
            # 파일 경로 생성
            new_filename = f"{volume}-{name.zfill(page_zfill)}{ext}"
            src = os.path.join(src_path, img)
            dst = os.path.join(dest_path, new_filename)
            images_name.append(new_filename)
            print("src: ", src)
            print("dst: ", dst)
            print("================================================")
            try:
                ...
                ##############################################################################################
                # shutil.copy2(src, dst)
                ##############################################################################################
            except Exception as e:
                msg = f"파일 복사 실패: {str(e)}"
                print(msg)
                for image in images_name:
                    os.remove(os.path.join(dest_path, image))
                return create_result_dict(mangas, msg, True, images_name, tags)
                continue
            
            ##############################################################################################
            # os.remove(src)
            ##############################################################################################
        volumes.append(volume)
        tags['title'] = tags['titles'] + manga.folder_name + '_'
    srcs_path = [src for src in srcs_path if src != dest_path]
    for src in srcs_path:
        imgs = [i for i in os.listdir(src) if os.path.isfile(os.path.join(src, i)) and get_extension(i) in IMG_EXT + ZIP_EXT]
        if not imgs:
            remove_folder(src)

    return create_result_dict(mangas[0], '폴더 병합 성공', True, images_name, tags)      
            
    # srcs_files = []
    # for src_path in srcs_path:
    #     src_files = []
    #     for file in os.listdir(src_path):
    #         if os.path.isfile(os.path.join(src_path, file)) and get_extension(file) in IMG_EXT + ZIP_EXT:
    #             src_files.append(file)
    #             volume_number = get_max_volume_number(file)
    #             if volume_number and int(volume_number) > max_volume_number:
    #                 max_volume_number = int(volume_number)
    #     zfill_count = get_max_file_number_length(src_files)
    #     if zfill_count > max_zfill_count:
    #         max_zfill_count = zfill_count
    #     srcs_files.append(src_files)   
        
    # for i, src_files in enumerate(srcs_files):
    #     for j, src_file in enumerate(src_files):
    #         basename = os.path.basename(src_file)   #   
    #         name, ext = os.path.splitext(basename)
    #         page = re.findall(r'\d+$', name)[0]  # 뒷부분 숫자 선택
    #         volume = re.findall(r'_?[\d]{2}-', name)[0].replace('_', '')  # 앞부분 숫자 선택
    #         title = re.sub(r'\d+$', '', name)
    #         title = re.sub(r'_?[\d]{2}-', '', title)
    #         new_filename = f"{title}_{str(i+1).zfill(volume_zfill)}-{page.zfill(max_zfill_count)}{ext}"
    #         print(new_filename)
    
    
    
    
    
    
    
    
    

    # result = []

    # # target_folder_name 처리
    # folder_parts = target_folder_name.split('/')
    # if len(folder_parts) > 1:
    #     # 상위 폴더가 genres_list에 있는지 확인
    #     genre_folder = folder_parts[0]
    #     if genre_folder not in get_genres_list():
    #         raise ValueError(f"Invalid genre folder: {genre_folder}")
        
    #     # 타이틀 폴더명 처리
    #     title_folder = del_specialCharacter(folder_parts[-1])[:200]
    #     folder_parts[-1] = title_folder
    #     target_folder_name = '/'.join(folder_parts)

    # target_path = os.path.join(BASE_PATH, target_folder_name)

    # # file_date가 가장 오래된 망가 찾기
    # oldest_manga = min(mangas, key=lambda x: x.file_date)

    # # 대상 폴더가 원본 폴더 중 하나인지 확인
    # reuse_original = any(
    #     os.path.normpath(os.path.join(BASE_PATH, manga.folder_name)) == os.path.normpath(target_path)
    #     for manga in mangas
    # )

    # if not reuse_original:
    #     if os.path.exists(target_path):
    #         # 새로운 경로 생성시에도 동일한 규칙 적용
    #         new_path = get_unique_path(target_path)
    #         folder_parts = os.path.relpath(new_path, BASE_PATH).split(os.sep)
    #         if len(folder_parts) > 1:
    #             folder_parts[-1] = del_specialCharacter(folder_parts[-1])[:200]
    #             target_path = os.path.join(BASE_PATH, *folder_parts)
    #         print(f"새로운 폴더명: {target_path}")
    #     os.makedirs(target_path)

    # # 각 망가 폴더의 파일 정보를 미리 수집
    # folder_files = []
    # # folder_name으로 정렬된 manga 리스트
    # sorted_mangas = sorted(mangas, key=lambda x: x.folder_name)

    # for manga in sorted_mangas:
    #     source_path = os.path.join(BASE_PATH, manga.folder_name)
    #     files = sorted(os.listdir(source_path))
    #     max_length = get_max_file_number_length(files)
    #     folder_files.append({
    #         'manga': manga,
    #         'files': files,
    #         'max_length': max_length,
    #         'source_path': source_path
    #     })

    # # 전체 폴더 중 가장 긴 숫자 길이 확인
    # max_prefix_length = max(info['max_length'] for info in folder_files)

    # # 모든 파일명을 모아서 정렬된 순서대로 처리하기 위한 리스트
    # all_files_info = []
    # for folder_index, folder_info in enumerate(folder_files):
    #     source_path = folder_info['source_path']
    #     prefix = str(folder_index).zfill(2)  # 00, 01, 02, ...
    #     print('prefix:', prefix)
    #     for file_name in folder_info['files']:
    #         if os.path.isfile(os.path.join(source_path, file_name)):
    #             filename, ext = os.path.splitext(file_name)
    #             number_match = re.match(r'^(\d+)', filename)
    #             if number_match:
    #                 number = int(number_match.group(1))
    #                 rest_filename = filename[len(number_match.group(1)):]
    #             else:
    #                 number = 0  # 숫자가 없는 경우 0으로 처리
    #                 rest_filename = filename
                
    #             all_files_info.append({
    #                 'original_name': file_name,
    #                 'source_path': source_path,
    #                 'number': number,
    #                 'rest_filename': rest_filename,
    #                 'ext': ext,
    #                 'prefix': prefix  # 폴더별 접두어 추가
    #             })

    # # 파일을 숫자 순서대로 정렬
    # all_files_info.sort(key=lambda x: (x['prefix'], x['number']))

    # # 새로운 파일명 목록을 저장할 리스트
    # new_filenames = []

    # # 모든 파일을 순차적으로 처리
    # for file_info in all_files_info:
    #     try:
    #         source_file = os.path.join(file_info['source_path'], file_info['original_name'])
            
    #         # 숫자 부분을 zfill로 패딩
    #         if file_info['number']:
    #             padded_number = str(file_info['number']).zfill(max_prefix_length)
    #         else:
    #             padded_number = str(1).zfill(max_prefix_length)
            
    #         # 대상 폴더와 상관없이 모든 파일에 대해 새 이름 생성
    #         new_name = f"{file_info['prefix']}{VOLUME_SEPARATOR}{padded_number}{file_info['rest_filename']}{file_info['ext']}"
    #         new_filenames.append(new_name)
            
    #         # 원본 파일이 대상 폴더에 있는 경우에도 같은 폴더에 새 이름으로 복사
    #         if os.path.normpath(file_info['source_path']) == os.path.normpath(target_path):
    #             old_file = os.path.join(target_path, file_info['original_name'])
    #             new_file = os.path.join(target_path, new_name)
    #             if old_file != new_file:  # 같은 파일이 아닌 경우에만 복사
    #                 shutil.copy2(old_file, new_file)
    #                 os.remove(old_file)  # 원본 파일 삭제
    #         else:
    #             # 다른 폴더의 파일은 새 이름으로 복사
    #             dest_file = os.path.join(target_path, new_name)
    #             shutil.copy2(source_file, dest_file)
        
    #     except Exception as e:
    #         msg = f"파일 복사 실패: {str(e)}"
    #         print(msg)
    #         continue

    # # 원본 폴더 삭제 (대상 폴더가 아닌 경우만)
    # for folder_info in folder_files:
    #     source_path = folder_info['source_path']
    #     if os.path.normpath(source_path) != os.path.normpath(target_path):
    #         try:
    #             os.rmdir(source_path)
    #         except OSError:
    #             shutil.rmtree(source_path)

    # # manga 모델 업데이트
    # for folder_info in folder_files:
    #     manga = folder_info['manga']
    #     try:
    #         if manga.id == oldest_manga.id:
    #             manga.folder_name = get_relative_path(target_path)
    #             img_exp_list = IMG_EXT + ZIP_EXT
    #             manga.images_list = json.dumps([os.path.basename(i) for i in new_filenames if os.path.isfile(i) and i[i.rfind('.')+1:].lower() in img_exp_list])
    #             print('manga.images_list:', manga.images_list)
    #             manga.update_date = datetime.now(KST)
    #             manga.page = len(new_filenames)
    #             msg = f"폴더 병합 성공 (유지됨): {folder_info['source_path']} -> {target_path}"
    #         else:
    #             msg = f"폴더 병합 성공 (삭제됨): {folder_info['source_path']} -> {target_path}"
            
    #         result.append(create_result_dict(manga, msg, True))
            
    #     except Exception as e:
    #         msg = f"폴더 병합 실패: {str(e)}"
    #         result.append(create_result_dict(manga, msg, False))

    # return result

























def rename_images_name(folder_name, images_name):
    if len(images_name) == 0:
        return False
    
    images_name.sort()
    
    for i, img_name in enumerate(images_name):
        img_path = os.path.join(BASE_PATH, folder_name, img_name)
        if os.path.isfile(img_path):
            img_path_new = os.path.join(BASE_PATH, folder_name, str(i).zfill(zfill_count) + '.' + img_path.split('.')[-1])
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