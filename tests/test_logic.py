import os

import pytest


@pytest.fixture(autouse=True)
def test_engine():
    test_path = '/tmp/test_english_bot_db.sqlite'
    os.environ['ENGLISH_BOT_DB_PATH'] = 'sqlite:///{}'.format(test_path)
    from english_cards.db import engine
    engine.init()
    yield engine
    os.remove(test_path)


def _add_word(name, translate):
    from english_cards.logic import add_word
    return add_word(name=name, translate=translate)


@pytest.fixture
def word():
    return _add_word(name='test', translate='test_translate')


@pytest.fixture
def words():
    return [_add_word(name='test_{}'.format(n),
                      translate='test_{}_translate'.format(n))
            for n in range(10)]


def test_add_word():
    from english_cards.logic import add_word
    word = add_word('test', 'test_translate')

    assert word.id == 1
    assert word.name == 'test'
    assert word.translate == 'test_translate'


@pytest.mark.usefixtures('word')
def test_add_duplicated_word():
    from english_cards.logic import (
        add_word,
        LogicError
    )

    with pytest.raises(LogicError):
        add_word(
            name='test',
            translate='test_translate'
        )


@pytest.mark.parametrize('count', [2, 3, 4, 5])
@pytest.mark.usefixtures('words')
def test_get_quest(count):
    from english_cards.logic import get_quest
    quest_word, translate_variants = get_quest(count)
    assert quest_word is not None
    assert len(translate_variants) == count
    assert quest_word.translate in translate_variants


def test_get_quest_count_one():
    from english_cards.logic import (
        get_quest,
        LogicError
    )

    with pytest.raises(LogicError):
        get_quest(1)
