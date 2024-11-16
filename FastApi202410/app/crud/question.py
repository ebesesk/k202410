from datetime import datetime

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.schemas.question import QuestionCreate, QuestionUpdate

from app.models.question import Question
from app.models.user import User
from app.models.answer import Answer
import re

def get_question_list(db: Session, user:User, skip: int = 0, limit: int = 10, keyword: str = ''):
    question_list = db.query(Question)
    # print(User.id)
    # print(skip, limit, keyword)
    search = '%{}%'.format(keyword)
    sub_query = db.query(Answer.question_id, Answer.content, User.username) \
        .outerjoin(User, Answer.user_id == User.id).subquery()
    
    if user.username != 'kds':
        search_tags = [Question.subject.ilike(tag) for tag in ['#쿼리#%', '#admin#%']]
        search = re.sub(r'^#[^#]+#', '', keyword)
        question_list = question_list \
        .outerjoin(User) \
        .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
        .filter(
                (Question.subject.ilike(search) |  # 질문제목
                Question.content.ilike(search) |  # 질문내용
                User.username.ilike(search) |  # 질문작성자
                sub_query.c.content.ilike(search) |  # 답변내용
                sub_query.c.username.ilike(search))  # 답변작성자
                & ~or_(*search_tags)
                )
    else:
        print('search', search)
        question_list = question_list \
            .outerjoin(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(
                    Question.subject.ilike(search) |  # 질문제목
                    Question.content.ilike(search) |  # 질문내용
                    User.username.ilike(search) |  # 질문작성자
                    sub_query.c.content.ilike(search) |  # 답변내용
                    sub_query.c.username.ilike(search)  # 답변작성자
                    )
    total = question_list.distinct().count()
    question_list = question_list.order_by(Question.create_date.desc()) \
        .offset(skip).limit(limit).distinct().all()
    # print(total, question_list)
    # for q in question_list:
    #     print(q.subject)
    return total, question_list  # (전체 건수, 페이징 적용된 질문 목록)


def get_question(db: Session, question_id: int):
    question = db.query(Question).get(question_id)
    return question


def create_question(db: Session, 
                    question_create: QuestionCreate, 
                    user: User):
    # print(user.username)
    if user.username == 'kds' or user.username == 'kdds':
        _subject = question_create.subject
    else:
        _subject = re.sub(r'^#[^#]+#', '', question_create.subject)
    
    db_question = Question(subject= _subject,
                            content=question_create.content,
                            create_date=datetime.now(),
                            user=user)
    db.add(db_question)
    db.commit()


def update_question(db: Session, user: User, db_question: Question,
                    question_update: QuestionUpdate):
    c = r'^#[a-zA-Z0-9가-힣]{2,5}+#'
    _class = re.findall(c, question_update.subject)
    if _class and user.username == 'kds' and user.username == 'kdds':
        db_question.subject = question_update.subject
    else:
        _subject = re.sub(c, '', question_update.subject)
        db_question.subject = question_update.subject
    db_question.content = question_update.content
    db_question.modify_date = datetime.now()
    db.add(db_question)
    db.commit()


def delete_question(db: Session, db_question: Question):
    db.delete(db_question)
    db.commit()


def vote_question(db: Session, db_question: Question, db_user: User):
    db_question.voter.append(db_user)
    db.commit()


# async examples
async def get_async_question_list(db: Session):
    data = await db.execute(select(Question)
                            .order_by(Question.create_date.desc())
                            .limit(10))
    return data.all()


async def async_create_question(db: Session, question_create: QuestionCreate):
    db_question = Question(subject=question_create.subject,
                           content=question_create.content,
                           create_date=datetime.now())
    db.add(db_question)
    await db.commit()