from typing import Any
from sqlalchemy.ext.declarative import declared_attr, declarative_base

class CustomBase:
    id: Any
    __name__: str

    # 테이블명을 자동으로 클래스명의 소문자로 생성
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

Base = declarative_base(cls=CustomBase)