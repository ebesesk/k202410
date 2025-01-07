from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.utils.dependencies import (
    get_current_user,
    get_db
)
from app.models.user import User

from app.schemas.answer import Answer, AnswerCreate, AnswerUpdate, AnswerDelete
from app.crud import answer as crud
from app.crud import question as question_crud

router = APIRouter()


@router.post("/create/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def answer_create(question_id: int,
                  _answer_create: AnswerCreate,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):

    # create answer
    question = question_crud.get_question(db, question_id=question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    crud.create_answer(db, question=question,
                              answer_create=_answer_create,
                              user=current_user)


@router.get("/detail/{answer_id}", response_model=Answer)
def answer_detail(answer_id: int,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user),
                  ):
    answer = crud.get_answer(db, answer_id=answer_id)
    return answer


@router.put("/update", status_code=status.HTTP_204_NO_CONTENT)
def answer_update(_answer_update: AnswerUpdate,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    db_answer = crud.get_answer(db, answer_id=_answer_update.answer_id)
    if not db_answer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을수 없습니다.")
    if current_user.id != db_answer.user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="삭제 권한이 없습니다.")
    crud.update_answer(db=db, db_answer=db_answer,
                              answer_update=_answer_update)


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def answer_delete(_answer_delete: AnswerDelete,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    db_answer = crud.get_answer(db, answer_id=_answer_delete.answer_id)
    if not db_answer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을수 없습니다.")
    if current_user.id != db_answer.user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="삭제 권한이 없습니다.")
    crud.delete_answer(db=db, db_answer=db_answer)


# @router.post("/vote", status_code=status.HTTP_204_NO_CONTENT)
# def answer_vote(_answer_vote: schema.AnswerVote,
#                 db: Session = Depends(get_db),
#                 current_user: User = Depends(get_current_user)):
#     db_answer = crud.get_answer(db, answer_id=_answer_vote.answer_id)
#     if not db_answer:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
#                             detail="데이터를 찾을수 없습니다.")
#     crud.vote_answer(db, db_answer=db_answer, db_user=current_user)
