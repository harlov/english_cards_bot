from sqlalchemy.sql.expression import func
from sqlalchemy.exc import IntegrityError

from english_cards.db import get_session
from english_cards.model import Word


class LogicError(Exception):
    pass


def add_word(name, translate):
    session = get_session()
    word = Word()

    word.name = name
    word.translate = translate

    session.add(word)

    try:
        session.commit()
    except IntegrityError:
        raise LogicError('word "{}" already exist!'.format(name))

    return word


def get_random_word():
    session = get_session()
    return session.query(Word).order_by(func.random()).first()
