import re, os
from typing import List, Tuple

def del_specialCharacter(text):
    text = text.strip()
    patterns = [
        r'[|\\{}]',          # 파이프와 중괄호
        r'[\[\]/?]',         # 대괄호와 슬래시
        r'[.,;:!]',          # 구두점
        r'[*~`^]',           # 특수 기호
        r'[+<>@#$%&=]',      # 연산자와 특수 문자
        r'[\'\"]',           # 따옴표
        r'[-_]',             # 하이픈과 언더스코어
        r'\s+',              # 연속 공백
        r'_+',               # 언더스코어
    ]   
    for pattern in patterns:
        text = re.sub(pattern, ' ', text)
    text = text.strip().replace(' ', '_')
    return text

def get_unique_path(base_path: str) -> str:
    """중복되지 않는 경로를 찾아서 반환합니다."""
    if not os.path.exists(base_path):
        return base_path
        
    counter = 1
    while True:
        new_path = f"{base_path} ({counter})"
        if not os.path.exists(new_path):
            return new_path
        counter += 1

def get_max_file_number_length(files: List[str]) -> int:
    """
    파일 목록에서 숫자로 시작하는 가장 긴 숫자의 길이를 반환합니다.
    
    Args:
        files: 파일명 리스트
        
    Returns:
        int: 가장 긴 숫자의 길이
    """
    max_length = 1  # 기본값
    for filename in files:
        # 파일명에서 숫자부분만 추출
        number_match = re.match(r'^(\d+)', filename)
        if number_match:
            max_length = max(max_length, len(number_match.group(1)))
    return max_length

def move_folder(source_path: str, target_path: str) -> Tuple[bool, str]:
    """
    폴더를 이동합니다.
    
    Args:
        source_path: 이동할 폴더 경로
        target_path: 이동 대상 경로
        
    Returns:
        Tuple[bool, str]: (성공 여부, 메시지)
    """
    try:
        if os.path.exists(target_path):
            msg = f"이미 존재하는 폴더입니다: {target_path}"
            print(msg)
            return False, msg
        
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        os.rename(source_path, target_path)
        
        msg = f"폴더 이동 성공: {source_path} -> {target_path}"
        print(msg)
        return True, msg
        
    except Exception as e:
        msg = f"폴더 이동 실패: {str(e)}"
        print(msg)
        return False, msg