from sqlalchemy.ext.declarative import (
    declarative_base,
    declared_attr
)

from sqlalchemy import (
    Column,
    Integer,
    String
)


class _BaseModel:
    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls):
        return '{}s'.format(cls.__name__.lower())


BaseModel = declarative_base(cls=_BaseModel)


class Word(BaseModel):
    name = Column(String, unique=True)
    translate = Column(String)
    balance = Column(Integer)
