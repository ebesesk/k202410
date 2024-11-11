import datetime
import sqlalchemy
from sqlalchemy import or_, and_, not_, except_, func
from sqlalchemy.orm import Session
from app.schemas import video as video_schema

from app.models.video import Video

# def join_Video_voter(db: Session):
#     return db.query(Video).join(video_voter).all()

def get_video_id(db:Session, video_id:int):
    return db.query(Video).get(video_id)

def get_all_videos(db: Session):
    # print(db.query(Video).all())
    return db.query(Video).all()


def del_dbid(db: Session, dbid: str):
    video = db.query(Video).filter(Video.dbid == dbid)
    if not video.first():
        return f'{dbid} db 없음'
    video.delete(synchronize_session=False)
    db.commit()

def input_videoinfo(db: Session, q: video_schema.Video_update):
    video = db.query(Video).filter(Video.id == q['id'])
    q['date_modified'] = datetime.datetime.now()
    video.update(q)
    db.commit()
    
def create_new_video(db: Session, _video: video_schema.Video_create):
    _video['date_posted'] = datetime.datetime.now()
    # print(_video)
    video = Video(**_video)
    db.add(video)
    db.commit()
    db.refresh(video)
    
def get_video_list(db: Session, skip:int=0, limit:int=0, keyword:str=""):
    _video_list = db.query(Video).filter(
        or_(Video.dbid.ilike("%"+keyword+"%"), Video.etc.ilike("%"+keyword+"%"))
        ).order_by(Video.date_posted.desc())
    total = _video_list.count()
    video_list = _video_list.offset(skip).limit(limit).all()
    return total, video_list
    
# def vote_video(db: Session, db_video: Video, db_user:User):
#     db_video.voter.append(db_user)
#     db.commit()
    
# def delete_vote(db:Session, db_video: Video, db_user:User):
#     db_video.voter.remove(db_user)
#     db.commit()

# def dislike_video(db: Session, db_video: Video, db_user: User):
#     db_video.dislike.append(db_user)
#     db.commit()

# def delete_dislike(db: Session, db_video: Video, db_user: User):
#     db_video.dislike.remove(db_user)
#     db.commit()

def get_keyword(db:Session):
    return db.query(Video.etc).filter(Video.etc.is_not(None)).all()
    
    
def search_video(db: Session, keyword, skip:int=0, limit:int=0):
    # print(keyword)
    q = []
    q_except = []
    j = 0
    # print(keyword)
    if ('resolution' in keyword) and (len(keyword['resolution']) > 0):
        _q = []
        for value in keyword['resolution']:
            if value == 'high':
                _q.append((Video.width * Video.height) >= 786432)
            elif value == 'middle':
                _q.append(and_(((Video.width * Video.height) < 786432), ((Video.width * Video.height) > 307200)))
            elif value == 'low':
                _q.append((Video.width * Video.height) <= 307200)
            else:
                continue
        if 'not' not in keyword['resolution']:
            q.append(or_(*_q))
        else:
            q.append(not_(or_(*_q)))


    if ('display_quality' in keyword) and (len(keyword['display_quality']) > 0):
        _q = []
        for value in keyword['display_quality']:
            if value == 'not':
                _q.append(Video.display_quality.is_(None))
            else:
                _q.append(Video.display_quality == value)
        q.append(or_(*_q))
 
            
    if ('country' in keyword) and (len(keyword['country']) > 0):
        _q = []
        for value in keyword['country']:
            if value=='not':
                _q.append(Video.country == None)
                # _q.append(Video.country.is_(None))
            else:
                _q.append(Video.country == value)
        q.append(or_(*_q))
                

    if ('face' in keyword) and (len(keyword['face']) > 0):
        _q = []
        for value in keyword['face']:
            if value=='not':
                _q.append(Video.face.is_(None))
            else:
                _q.append(Video.face == value)
        q.append(or_(*_q))


    if ('look' in keyword) and (len(keyword['look']) > 0):
        _q = []
        for value in keyword['look']:
            if value=='not':
                _q.append(Video.look.is_(None))
            else:
                _q.append(Video.look == value)
        q.append(or_(*_q))



    if ('age' in keyword) and (len(keyword['age']) > 0):
        _q = []
        for value in keyword['age']:
            if value=='not':
                _q.append(Video.age.is_(None))
            else:
                _q.append(Video.age == value)
        q.append(or_(*_q))



    if ('pussy' in keyword) and (len(keyword['pussy']) > 0):
        _q = []
        for value in keyword['pussy']:
            if value=='not':
                _q.append(Video.pussy.is_(None))
            else:
                _q.append(Video.pussy == value)
        q.append(or_(*_q)) 


    if ('etc' in keyword) and (len(keyword['etc']) > 0):
        _q = []
        # q_ = []
        if '#not' in keyword['etc']:
            i = keyword['etc'].index('#not')
            # keyword['etc'].remove('not')
            for value in keyword['etc'][:i]:
                search = '%{}%'.format(value)
                _q.append(
                    or_(Video.etc.ilike(search), Video.dbid.ilike(search))
                )
            for value in keyword['etc'][i+1:]:
                if value != '':
                    search = '%{}%'.format(value)
                    q_except.append(
                        or_(Video.etc.ilike(search), Video.dbid.ilike(search))
                        # or_(not_(Video.etc.ilike(search)), not_(Video.dbid.ilike(search)))
                    )
        else:
            for value in keyword['etc']:
                # print(value, 'else')
                search = '%{}%'.format(value)
                _q.append(
                    or_(Video.etc.ilike(search), Video.dbid.ilike(search))
                )
        # _q.append(Video.etc == None)
        q.append(or_(*_q))


    if 'ad_start' in keyword:
        _q = []
        if keyword['ad_start'] == True:
            _q.append(Video.ad_start.isnot(None))
        elif keyword['ad_start'] == False:
            _q.append(Video.ad_start.is_(None))
        q.append(or_(*_q))
            
    if 'star' in keyword:
        _q = []
        if keyword['star'] == None:
            _q.append(Video.star.is_(None))
        elif keyword['star'] == True:
            _q.append(Video.star.isnot(None))
        elif keyword['star'] == '1':
            _q.append(Video.star == 1)
        elif keyword['star'] == '2':
            _q.append(Video.star == 2)
        elif keyword['star'] == '3':
            _q.append(Video.star == 3)
        elif keyword['star'] == '4':
            _q.append(Video.star == 4)
        elif keyword['star'] == '5':
            _q.append(Video.star == 5)
        q.append(or_(*_q))
        
        
    
    if 'school_uniform' in keyword:
        if keyword['school_uniform'] == True:
            q.append(Video.school_uniform == True)
        elif keyword['school_uniform'] == False:
            # q.append(Video.school_uniform != True)
            q.append(Video.school_uniform.isnot(True))
    
    
    if 'hip' in keyword:
        if keyword['hip'] == True:
            q.append(Video.hip == True)
        elif keyword['hip'] == False:
            q.append(Video.hip.isnot(True))
    
    
    
    
    if 'group' in keyword:
        if keyword['group'] == True:
            q.append(Video.group == True)
        elif keyword['group'] == False:
            q.append(Video.group.isnot(True))
    
    
    if 'pregnant' in keyword:
        if keyword['pregnant'] == True:
            q.append(Video.pregnant == True)
        elif keyword['pregnant'] == False:
            q.append(Video.pregnant.isnot(True))
    
    
    if 'oral' in keyword:
        if keyword['oral'] == True:
            q.append(Video.oral == True)
        elif keyword['oral'] == False:
            q.append(Video.oral.isnot(True))
    
    
    if 'ani' in keyword:
        if keyword['ani'] == True:
            q.append(Video.ani == True)
        elif keyword['ani'] == False:
            q.append(Video.ani.isnot(True))
    
    
    if 'lesbian' in keyword:
        if keyword['lesbian'] == True:
            q.append(Video.lesbian == True)
        elif keyword['lesbian'] == False:
            q.append(Video.lesbian.isnot(True))
    
    
    if 'conversation' in keyword:
        if keyword['conversation'] == True:
            q.append(Video.conversation == True)
        elif keyword['conversation'] == False:
            q.append(Video.conversation.isnot(True))
            
    
    if 'masturbation' in keyword:
        if keyword['masturbation'] == True:
            q.append(Video.masturbation == True)
        elif keyword['masturbation'] == False:
            q.append(Video.masturbation.isnot(True))
    
    
    if 'massage' in keyword:
        if keyword['massage'] == True:
            q.append(Video.massage == True)
        elif keyword['massage'] == False:
            q.append(Video.massage.isnot(True))
    
    
    if 'uniform' in keyword:
        if keyword['uniform'] == True:
            q.append(Video.uniform == True)
        elif keyword['uniform'] == False:
            q.append(Video.uniform.isnot(True))
    
    
    if 'family' in keyword:
        if keyword['family'] == True:
            q.append(Video.family == True)
        elif keyword['family'] == False:
            q.append(Video.family.isnot(True))


    _video_list = db.query(Video).filter(and_(*q))
    # dislike_list = db.query(Video).join(video_dislike)  # dislike 추출
    # _video_list = _video_list.except_(dislike_list)     # dislike except
    if len(q_except) > 0:                               # or_ 빈리스트 입력되면 DB모두 선택 0보다 클경우만 
        except_list = db.query(Video).filter(or_(*q_except))
        _video_list = _video_list.except_(except_list)
    # if 'vote' in keyword and keyword['vote']:
    #     _video_list = _video_list.join(video_voter)
    # if 'dislike' in keyword and keyword['dislike']:
    #     _video_list = db.query(Video).join(video_dislike)
    
    if 'random' in keyword and keyword['random']:
        _video_list = _video_list.order_by(func.random())
        total = _video_list.count()
        video_list = _video_list.offset(skip).limit(limit).all()
        print(total)
        # print(video_list[0].school_uniform, '-3-3-3-3-3-3-')
        return total, video_list    
        
    _video_list = _video_list.order_by(Video.date_posted.desc())
    total = _video_list.count()
    video_list = _video_list.offset(skip).limit(limit).all()
    print(total)
    # print(video_list[0].school_uniform, '-3-3-3-3-3-3-')
    return total, video_list



# def search_video(db: Session, keyword, skip:int=0, limit:int=0):
#     # print(keyword)
#     q = []
#     j = 0
#     for _key in keyword:
#         j = j + 1
#         if type(keyword[_key]) == list:
#             if _key == 'resolution':
#                 if len(keyword[_key]) > 0:
#                     _q = []
#                     for value in keyword[_key]:
#                         if value == 'high':
#                             _q.append((Video.width * Video.height) >= 786432)
#                         elif value == 'middle':
#                             _q.append(and_(((Video.width * Video.height) < 786432), ((Video.width * Video.height) > 307200)))
#                         elif value == 'low':
#                             _q.append((Video.width * Video.height) <= 307200)
#                         else:
#                             continue
#                     if 'not' not in keyword[_key]:
#                         q.append(or_(*_q))
#                     else:
#                         q.append(not_(or_(*_q)))


#             elif _key == 'display_quality':
#                 if len(keyword[_key]) > 0:
#                     _q = []
#                     for value in keyword[_key]:
#                         _q.append(Video.display_quality == value)
#                     if 'not' not in keyword[_key]:
#                         q.append(or_(*_q))
#                     else:
#                         q.append(not_(or_(*_q)))

  
#             elif _key == 'country':
#                 if len(keyword[_key]) > 0:
#                     _q = []
#                     for value in keyword[_key]:
#                         _q.append(Video.country == value)
#                     if 'not' not in keyword[_key]:
#                         q.append(or_(*_q))
#                     else:
#                         q.append(not_(or_(*_q)))
                        

#             elif _key == 'face':
#                 if len(keyword[_key]) > 0:
#                     # print(j, _key, 'list')
#                     _q = []
#                     for value in keyword[_key]:
#                         _q.append(Video.face == value)
#                     if 'not' not in keyword[_key]:
#                         q.append(or_(*_q))
#                     else:
#                         q.append(not_(or_(*_q)))


#             elif _key == 'look':
#                 if len(keyword[_key]) > 0:
#                     # print(j, _key, 'list')
#                     _q = []
#                     for value in keyword[_key]:
#                         _q.append(Video.look == value)
#                     if 'not' not in keyword[_key]:
#                         q.append(or_(*_q))
#                     else:
#                         q.append(not_(or_(*_q)))


#             elif _key == 'age':
#                 if len(keyword[_key]) > 0:
#                     # print(j, _key, 'list')
#                     _q = []
#                     for value in keyword[_key]:
#                         _q.append(Video.age == value)
#                     if 'not' not in keyword[_key]:
#                         q.append(or_(*_q))
#                     else:
#                         q.append(not_(or_(*_q)))


#             elif _key == 'pussy':
#                 if len(keyword[_key]) > 0:
#                     # print(j, _key, 'list')
#                     _q = []
#                     for value in keyword[_key]:
#                         _q.append(Video.pussy == value)
#                     if 'not' not in keyword[_key]:
#                         q.append(or_(*_q))
#                     else:
#                         q.append(not_(or_(*_q)))


#             elif _key == 'etc':
#                 if len(keyword[_key]) > 0:
#                     _q = []
#                     if '#not' in keyword[_key]:
#                         i = keyword[_key].index('#not')
#                         # keyword[_key].remove('not')
#                         for value in keyword[_key][:i]:
#                             print(value)
#                             search = '%{}%'.format(value)
#                             _q.append(
#                                 or_(Video.etc.ilike(search), Video.dbid.ilike(search))
#                             )
#                         for value in keyword[_key][i+1:]:
#                             search = '%{}%'.format(value)
#                             _q.append(
#                                 or_(not_(Video.etc.ilike(search)), not_(Video.dbid.ilike(search)))
#                             )
#                     else:
#                         for value in keyword[_key]:
#                             # print(value, 'else')
#                             search = '%{}%'.format(value)
#                             _q.append(
#                                 or_(Video.etc.ilike(search), Video.dbid.ilike(search))
#                             )
#                     # _q.append(Video.etc == None)
#                     q.append(and_(*_q))


#         elif _key == 'ad_start':
#             _q = []
#             if keyword[_key] == True:
#                 _q.append(Video.ad_start != None)
#             elif keyword[_key] == False:
#                 _q.append(Video.ad_start == None)
#             q.append(or_(*_q))
                
#         elif _key == 'star':
#             _q = []
#             if keyword[_key] == None:
#                 _q.append(Video.star == None)
#             elif keyword[_key] == True:
#                 _q.append(Video.star != None)
#             elif keyword[_key] == '1':
#                 _q.append(Video.star == 1)
#             elif keyword[_key] == '2':
#                 _q.append(Video.star == 2)
#             elif keyword[_key] == '3':
#                 _q.append(Video.star == 3)
#             elif keyword[_key] == '4':
#                 _q.append(Video.star == 4)
#             elif keyword[_key] == '5':
#                 _q.append(Video.star == 5)
#             q.append(or_(*_q))
            
            
#         elif type(keyword[_key]) == bool:
            
            
#             if _key == 'school_uniform':
#                 if keyword[_key] == True:
#                     q.append(Video.school_uniform == True)
#                 elif keyword[_key] == False:
#                     # q.append(Video.school_uniform != True)
#                     q.append(Video.school_uniform.isnot(True))
            
            
#             if _key == 'hip':
#                 if keyword[_key] == True:
#                     q.append(Video.hip == True)
#                 elif keyword[_key] == False:
#                     q.append(Video.hip.isnot(True))
            
            
            
            
#             if _key == 'group':
#                 if keyword[_key] == True:
#                     q.append(Video.group == True)
#                 elif keyword[_key] == False:
#                     q.append(Video.group.isnot(True))
            
            
#             if _key == 'pregnant':
#                 if keyword[_key] == True:
#                     q.append(Video.pregnant == True)
#                 elif keyword[_key] == False:
#                     q.append(Video.pregnant.isnot(True))
            
            
#             if _key == 'oral':
#                 if keyword[_key] == True:
#                     q.append(Video.oral == True)
#                 elif keyword[_key] == False:
#                     q.append(Video.oral.isnot(True))
            
            
#             if _key == 'ani':
#                 if keyword[_key] == True:
#                     q.append(Video.ani == True)
#                 elif keyword[_key] == False:
#                     q.append(Video.ani.isnot(True))
            
            
#             if _key == 'lesbian':
#                 if keyword[_key] == True:
#                     q.append(Video.lesbian == True)
#                 elif keyword[_key] == False:
#                     q.append(Video.lesbian.isnot(True))
            
            
#             if _key == 'conversation':
#                 if keyword[_key] == True:
#                     q.append(Video.conversation == True)
#                 elif keyword[_key] == False:
#                     q.append(Video.conversation.isnot(True))
                    
            
#             if _key == 'masturbation':
#                 if keyword[_key] == True:
#                     q.append(Video.masturbation == True)
#                 elif keyword[_key] == False:
#                     q.append(Video.masturbation.isnot(True))
            
            
#             if _key == 'massage':
#                 if keyword[_key] == True:
#                     q.append(Video.massage == True)
#                 elif keyword[_key] == False:
#                     q.append(Video.massage.isnot(True))
            
            
#             if _key == 'uniform':
#                 if keyword[_key] == True:
#                     q.append(Video.uniform == True)
#                 elif keyword[_key] == False:
#                     q.append(Video.uniform.isnot(True))
            
            
#             if _key == 'family':
#                 if keyword[_key] == True:
#                     q.append(Video.family == True)
#                 elif keyword[_key] == False:
#                     q.append(Video.family.isnot(True))
            
    
    # if 'vote' in keyword and keyword['vote']:
    #     _video_list = db.query(Video).filter(and_(*q)).join(video_voter).order_by(Video.date_posted.desc())
    # else:
    #     _video_list = db.query(Video).filter(and_(*q)).order_by(Video.date_posted.desc())
    # total = _video_list.count()
    # video_list = _video_list.offset(skip).limit(limit).all()
    # print(total)
    # print(video_list[0].school_uniform, '-3-3-3-3-3-3-')
    # return total, video_list