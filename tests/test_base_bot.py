import pytest


@pytest.fixture
def telegram_object():
    from english_cards.base_bot import TelegramObject

    class _TestTelegramObject(TelegramObject):
        _sub_objects_extracted = False

        ID_FIELD = 'test_id_field'

        def _extract_sub_objects(self):
            self._sub_objects_extracted = True

    return _TestTelegramObject({
        'test_id_field': 'test_id_field_value',
        'test_property': 'test_property_value'
    })


def test_telegram_object_id_property(telegram_object):
    assert telegram_object.id == 'test_id_field_value'


def test_telegram_object_extract_sub_objects_called(telegram_object):
    assert telegram_object._sub_objects_extracted is True


def test_telegram_object_getattr_proxy(telegram_object):
    assert telegram_object.test_property == 'test_property_value'


def test_telegram_object_getattr_no_exist(telegram_object):
    with pytest.raises(KeyError):
        telegram_object.test_not_exist_property


def test_chat_object_factory():
    from english_cards.base_bot import Chat
    chat_first_create = Chat({
        'id': 'test_chat_id'
    })

    chat_second_create = Chat({
        'id': 'test_chat_id'
    })

    chat_other = Chat({
        'id': 'other_test_chat_id'
    })

    assert chat_first_create is chat_second_create
    assert chat_second_create is not chat_other


def test_chat_object_storage():
    from english_cards.base_bot import Chat
    chat_first_create = Chat({
        'id': 'test_chat_id'
    })

    chat_first_create.storage['test'] = 'test_value'

    chat_second_create = Chat({
        'id': 'test_chat_id'
    })

    assert chat_second_create.storage['test'] == 'test_value'
