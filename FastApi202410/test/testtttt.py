def get_current_user_with_grade(grade: int):
    def dependency(request: Request):
        current_user = request.state.user  # 여기서 실제 사용자 가져오는 로직으로 대체
        if current_user.grade >= grade:
            return current_user
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    return dependency

def dependency_wrapper():
    return get_current_user_with_grade(2)  # 예를 들어, GOLD 등급이 2라고 가정

current_user: User = Depends(dependency_wrapper)
