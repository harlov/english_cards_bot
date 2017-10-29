import random

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


def get_quest(count):
    session = get_session()
    quest_word = session.query(Word).order_by(func.random()).first()
    other_words = session.query(Word).filter(Word.id != quest_word.id).order_by(func.random()).limit(count-1).all()
    translate_variants = [word.translate for word in other_words + [quest_word]]
    random.shuffle(translate_variants)
    return quest_word, translate_variants
