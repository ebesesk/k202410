from fastapi import APIRouter, HTTPException, Depends, status, Request
from typing import List, Dict
from pathlib import Path
import json

    
from app.utils.dependencies import (
    get_current_user,
    get_db
)
from app.models.user import User
from sqlalchemy.orm import Session

from app.crud.rating import RatingCRUD
from app.crud.video import (get_all_videos, get_video_list, get_video_id, 
                         input_videoinfo, del_dbid, search_video, get_keyword,
                         )
from app.schemas.video import (Video_info, Video_info_list, Video_update, Video_etckey,
                           Video_dbids, Scanreturn, VideoRatingCreate)
from app.schemas.rating import VideoRatingResponse
# from models import Video
# from db.repository.users import create_new_user
from app.utils import video as video_util
from app.core.config import settings
from sqlalchemy.orm import Session
# from .stream_mp4 import range_requests_response

router =APIRouter()
VIDEO_DIR = settings.VIDEO_DIR



# Video.svelte 동영상홈
@router.get("/list", response_model=Video_info_list)
def get_list(db: Session = Depends(get_db),
             page: int = 0,
             size: int = 10,
             keyword: str = ''
            ):
    # print('keyword: ', keyword)
    total, video_list = get_video_list(db=db, skip=page*size, limit=size, keyword=keyword)
    return {
        'total': total,
        'video_list': video_list
    }


# VideoInfo.svelte
@router.get("/detail/{video_id}", response_model=Video_info)
def get_video(video_id: int, 
              db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    video = get_video_id(db=db, video_id=video_id)
    return video

@router.put("/input_videoinfo", status_code=status.HTTP_204_NO_CONTENT)
def input_modified_videoinfo(_video_info: Video_update, 
                             db:Session=Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    # from urllib.parse import unquote
    # _video_info.dbid = unquote(_video_info.dbid)
    video_info = {}
    for i, j in enumerate(_video_info):
        video_info[j[0]] = j[1]
        if j[1] == 'del':
            video_info[j[0]] = None
    # print(video_info)
    input_videoinfo(db=db, q=video_info)
    # return _video_info




# Scanfiles.svelte
@router.get("/scan_files", response_model=Scanreturn)
def file_scan(db: Session=Depends(get_db),
              current_user: User = Depends(get_current_user)):
    # video_util.scan_files(db)
    return video_util.scan_files(db)




# @router.post("/add_dbids")
# def add_files_to_dbids(db: Session=Depends(get_db),
#                        detect_files: Addfiles=[]):
#     print(detect_files)
#     # video_util.add_dbids(db, detect_files)
#     # return video_util.add_dbids(db)

@router.get("/keywords", response_model=Video_etckey)
def get_keyword_db(db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    
    keywords = []
    for key in get_keyword(db):
        for i in key:
            if (i.strip() not in keywords) and (i.strip() != ''):
                keywords.append(i.strip())
                # print(i.strip())
    keywords = list(set(keywords))
    # print('keywords', keywords)
    # for i in keywords:
    #     print(i)
    return {'keywords': keywords}

@router.post("/{video_id}/view")
def increment_video_view(
    video_id: int,
    db: Session = Depends(get_db)
):
    view_count = RatingCRUD.increment_view_count_video(db, video_id)
    if view_count is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"video_id": video_id, "view_count": view_count}

# Search.svelte
@router.get("/search", response_model=Video_info_list)
def get_search(db: Session=Depends(get_db),
               current_user: User = Depends(get_current_user),
               page: int = 0,
               size: int = 10,
               keyword:str=''):
    if isinstance(keyword, str):
        try:
            # 문자열을 딕셔너리로 변환
            keyword = json.loads(keyword)
            # print('딕셔너리로 변환')
        except json.JSONDecodeError as e:
            print("문자열을 딕셔너리로 변환하는 중 오류 발생:", e)
            keyword = {'etc':"test"}
            # return {"error": "Invalid keyword format"}

    if ('etc' in keyword) and (len(keyword['etc']) > 0):
        keyword['etc'] = keyword['etc'].strip().split(',')
        keyword['etc'] = [i.strip() for i in keyword['etc']]
        # keyword['etc'].remove('')
    # 빈값 삭제
    keyword_copy = keyword.copy()
    for k in keyword_copy:
        if type(keyword[k]) == list and len(keyword[k]) == 0 :
            del keyword[k]
    print(keyword)
    total, video_list = search_video(db=db, keyword = keyword, user=current_user, skip=page*size, limit=size)
    # total, video_list = search_video(db=db, keyword = keyword, skip=page*size, limit=size)
    # print(total, video_list, page)
    # for video in video_list:
    #     print(video.__dict__)

    return {
        'total': total,
        'video_list': video_list
    }
    
@router.post("/{video_id}/rate")
def rate_video(
    video_id: int,
    rating_data: VideoRatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """비디오에 평점을 부여합니다."""
    video = get_video_id(db=db, video_id=video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    RatingCRUD.add_or_update_video_rating(
        db, current_user.id, video_id, rating_data.rating
    )
    return {"message": "Rating added successfully"}

@router.get("/{video_id}/rating", response_model=VideoRatingResponse)
def get_video_rating(video_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """비디오의 평점을 가져옵니다."""
    rating = RatingCRUD.get_video_rating(db=db, user_id=current_user.id, video_id=video_id)
    # print('current_user.id:', current_user.id, 'video_id:', video_id, {"rating": rating})

    if rating is None:
        # 평점이 없을 경우 기본값을 설정하거나 적절한 응답을 반환
        return {"rating":0}
    else:
        # print(VideoRatingResponse(rating))
        print(rating.video_id, rating.rating)
        # Pydantic 모델로 변환하여 반환
        return {'rating':rating.rating}

# @router.post("/vote", status_code=status.HTTP_204_NO_CONTENT)
# def video_vote(_video_vote: VideoVote,
#                db: Session = Depends(get_db),
#                current_user: User = Depends(get_current_user)):
#     db_video = get_video_id(db, video_id=_video_vote.video_id)
#     if not db_video:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
#                             detail="데이터를 찾을수 없습니다.")
#     vote_video(db=db, 
#                db_video=db_video, 
#                db_user=current_user)

# @router.delete("/delvote", status_code=status.HTTP_204_NO_CONTENT)
# def video_delete_voted(_video_vote: VideoVote,
#                        db: Session = Depends(get_db),
#                        current_user: User = Depends(get_current_user)):
#     db_video = get_video_id(db = db,
#                             video_id = _video_vote.video_id)
#     if not db_video:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
#                             detail = "데이터를 찾을수 없습니다.")
#     delete_vote(db = db, 
#                 db_video = db_video, 
#                 db_user = current_user)
        
# @router.post('/dislike', status_code=status.HTTP_204_NO_CONTENT)
# def video_dislike(_video_dislike: VideoDislike,
#                   db: Session = Depends(get_db),
#                   current_user: User = Depends(get_current_user)):
#     db_video = get_video_id(db, video_id=_video_dislike.video_id)
#     if not db_video:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
#                             detail="데이터를 찾을수 없습니다.")
#     dislike_video(db=db, 
#                   db_video=db_video, 
#                   db_user=current_user)

# @router.delete("/deldislike", status_code=status.HTTP_204_NO_CONTENT)
# def video_delete_dislike(_video_dislike: VideoDislike,
#                          db: Session = Depends(get_db),
#                          current_user: User = Depends(get_current_user)):
#     db_video = get_video_id(db=db, video_id=_video_dislike.video_id)
#     if not db_video:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
#                             detail="데이터를 찾을수 없습니다.")
#     delete_dislike(db=db, 
#                    db_video=db_video, 
#                    db_user=current_user)

# @router.get("/all", response_model=list[Video_info])
# def view_all(db: Session=Depends(get_db)):
    #     videos = get_all_videos(db)
#     return videos





    










@router.get("/stream")
def get_video(request: Request, dbid: str):
    video_path = Path(settings.VIDEO_DIR + dbid)
    return range_requests_response(request, file_path=video_path, content_type="video/mp4")


'''
['/home/video/yadong/20230214/video_2.ts',
 '/home/video/yadong/20230214/Twenty five Japanese women sucking and fucking in one room - IN3X.NET.ts',
 '/home/video/yadong/20230214/MUSUME-122922_01 The year-end party after a long time i_2.ts',
 '/home/video/yadong/20230214/FC2-PPV-1728678 [No appearance] play busty shaved activ.ts',
 '/home/video/yadong/20230214/JAV Hardcore Orgy Sex - 야동코리아.ts',
 '/home/video/yadong/20230214/엉덩이에 눈이 [2분 22초] - 한국야동 - 야동 무료야동 - 야팡.ts',
 '/home/video/yadong/20230214/FC2-PPV-3177333 980pt until 2_7 [Twice creampie] almost.ts',]

'''