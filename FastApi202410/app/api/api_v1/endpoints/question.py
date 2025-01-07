from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status 

# from . import schema, crud
from app.crud import question as crud
from app.schemas.question import QuestionList, Question, QuestionCreate, QuestionDelete, QuestionUpdate
from app.utils.dependencies import (
    get_current_user,
    get_db
)   
from app.models.user import User

router = APIRouter()


@router.get("/list", response_model=QuestionList)
def question_list(db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user),
                  page: int = 0, size: int = 10, keyword: str = ''):
    total, _question_list = crud.get_question_list(
        db, current_user, skip=page * size, limit=size, keyword=keyword)
    return {
        'total': total,
        'question_list': _question_list
    }


@router.get("/detail/{question_id}", response_model=Question)
def question_detail(question_id: int, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user),
                    ):
    question = crud.get_question(db, question_id=question_id)
    return question


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def question_create(_question_create: QuestionCreate,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user),):
    
    # if current_user.username == 'kds' or current_user.username == 'kdds':
    crud.create_question(db=db, 
                         question_create=_question_create,
                        user=current_user)


@router.put("/update", status_code=status.HTTP_204_NO_CONTENT)
def question_update(_question_update: QuestionUpdate,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):

    db_question = crud.get_question(db, question_id=_question_update.question_id)
    if not db_question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을수 없습니다.")
    if current_user.id != db_question.user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="수정 권한이 없습니다.")
    crud.update_question(db=db, user=current_user, db_question=db_question,
                                  question_update=_question_update)


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def question_delete(_question_delete: QuestionDelete,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    
    db_question = crud.get_question(db, question_id=_question_delete.question_id)
    if not db_question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을수 없습니다.")
    if current_user.id != db_question.user.id and current_user.points < 2000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="삭제 권한이 없습니다.")
    crud.delete_question(db=db, db_question=db_question)





# @router.post("/vote", status_code=status.HTTP_204_NO_CONTENT)
# def question_vote(_question_vote: QuestionVote,
#                   db: Session = Depends(get_db),
#                   current_user: User = Depends(get_current_user)):
#     db_question = crud.get_question(db, question_id=_question_vote.question_id)
#     if not db_question:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
#                             detail="데이터를 찾을수 없습니다.")
#     crud.vote_question(db, db_question=db_question, db_user=current_user)


# # async examples
# @router.get("/async_list")
# async def async_question_list(db: Session = Depends(get_async_db)):
#     result = await crud.get_async_question_list(db)
#     return result


# @router.post("/async_create", status_code=status.HTTP_204_NO_CONTENT)
# async def async_question_create(_question_create: schema.QuestionCreate,
#                                 db: Session = Depends(get_async_db)):
#     await crud.async_create_question(db, question_create=_question_create)