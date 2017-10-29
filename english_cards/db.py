import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from english_cards.model import BaseModel


class Engine:
    _engine = None

    def set_engine(self):
        self._engine = create_engine(os.environ.get('ENGLISH_BOT_DB_PATH') or
                                     'sqlite:////var/lib/english_cards/db.sqlite')

    def create_tables(self):
        BaseModel.metadata.create_all(self._engine)

    def init(self):
        self.set_engine()
        self.create_tables()

    def __getattr__(self, item):
        return getattr(self._engine, item)


engine = Engine()

Session = sessionmaker(bind=engine)


def get_session():
    return Session()
