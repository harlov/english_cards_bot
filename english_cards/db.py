from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from english_cards.model import BaseModel

engine = create_engine('sqlite:////var/lib/english_cards/db.sqlite')

BaseModel.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


def get_session():
    return Session()
