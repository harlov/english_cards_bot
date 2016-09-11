from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.exc import NoResultFound


class BaseEntity():
    @classmethod
    def add_or_get_by_field(cls, field, record):
        try:
            check_record = session.query(cls).filter(getattr(cls, field) == getattr(record, field)).one()
        except NoResultFound:
            session.add(record)
            session.commit()
            return record

        return check_record

Base = declarative_base(cls=BaseEntity)


class TelegramUser(Base):
    __tablename__ = 'telegram_user'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)

    @classmethod
    def get_telegram_user(cls, chat_id):
        return cls.add_or_get_by_field('chat_id', TelegramUser(chat_id=chat_id))


class UserDictionary(Base):
    __tablename__ = 'user_dictionary'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('telegram_user.id'))
    user = relationship(TelegramUser)
    word = Column(String, nullable=False)
    translation = Column(String, nullable=False)

    @classmethod
    def get_random_word(cls, user):
        return session.query(cls).filter(cls.user == user).order_by(func.random()).first()


engine = create_engine('sqlite:///english_cards.db')
DBSession = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

session = DBSession()