import types
import json

import requests

from english_cards.logger import logger


class TelegramFormatError(Exception):
    pass


class TelegramObject:
    ID_FIELD = 'id'

    def __init__(self, input_data):
        self._input_data = input_data
        self._extract_sub_objects()

    def _extract_sub_objects(self):
        pass

    @property
    def id(self):
        try:
            return self._input_data[self.ID_FIELD]
        except KeyError:
            raise TelegramFormatError('Object {} input data has no ID field "{}"'.format(self, self.ID_FIELD))

    def __getattr__(self, item):
        return self._input_data[item]


class Chat(TelegramObject):
    _chats_cache = dict()

    def __new__(cls, *args, **kwargs):
        data = args[0]
        try:
            chat_id = data['id']
        except KeyError:
            raise TelegramFormatError('Chat id not found in "{}"'.format(data))

        if chat_id not in cls._chats_cache:
            logger.debug('Create chat for <{}>'.format(chat_id))
            cls._chats_cache[chat_id] = super().__new__(cls)
            cls._chats_cache[chat_id].storage = dict()
            cls._chats_cache[chat_id].route_state = {
                'conversation': None
            }

        return cls._chats_cache[chat_id]

    def __init__(self, input_data):
        super(Chat, self).__init__(input_data)


class Message(TelegramObject):
    ID_FIELD = 'message_id'

    def _extract_sub_objects(self):
        try:
            self.chat = Chat(self.chat)
        except KeyError:
            raise TelegramFormatError('Message has invalid format: chat not found.')


def keyboard_item(text, request_contact=False, request_location=False):
    return {
        'text': text,
        'request_contact': request_contact,
        'request_location': request_location
    }


def replay_keyboard_markup(items=None, one_time_keyboard=True):
    if not items:
        return {
            'remove_keyboard': True
        }
    else:
        return {
            'keyboard': items,
            'one_time_keyboard': one_time_keyboard
        }


class Update(TelegramObject):
    ID_FIELD = 'update_id'

    def __init__(self, input_data, bot):
        self.bot = bot
        super(Update, self).__init__(input_data)

    def _extract_sub_objects(self):
        try:
            self.message = Message(self._input_data['message'])
        except KeyError:
            raise TelegramFormatError('Update has invalid format: message not found.')

    def reply(self, text, reply_markup=None):
        args = {
            'chat_id': self.message.chat.id,
            'text': text
        }
        if reply_markup:
            args['reply_markup'] = reply_markup

        self.bot.send_message(**args)

    @property
    def user_storage(self):
        return self.message.chat.storage

    @property
    def route_state(self):
        return self.message.chat.route_state


class Bot:
    BASE_URL = 'https://api.telegram.org/bot'
    POOLING_TIMEOUT = 60

    def _call_method(self, method, params=None):
        request_url = '{}{}/{}'.format(self.BASE_URL, self._api_key, method)
        return requests.get(url=request_url, params=params)

    def __init__(self, api_key, router):
        self._api_key = api_key
        self._router = router
        self._offset = 0

    def process_update(self, update_data):
        try:
            update = Update(update_data, self)
            self._router.handle(self, update)
        except TelegramFormatError as err:
            logger.error('Telegram format error: {}'.format(err))
        except Exception as err:
            logger.error('Unknown error: {}'.format(err))
        finally:
            self._offset = update_data['update_id'] + 1

    def run(self):
        while True:
            update_response = self._call_method('getUpdates', {
                'timeout': self.POOLING_TIMEOUT,
                'offset': self._offset
            })
            if not update_response.status_code == 200:
                continue

            update_object = update_response.json()

            if not update_object['ok']:
                continue

            update_items = update_object['result']

            for item in update_items:
                self.process_update(item)

    def send_message(self, chat_id, text, reply_to_message_id=None, reply_markup=None):
        params = {
            'chat_id': chat_id,
            'text': text
        }
        if reply_to_message_id:
            params['reply_to_message_id'] = reply_to_message_id

        if reply_markup:
            params['reply_markup'] = json.dumps(reply_markup)

        res = self._call_method('sendMessage', params=params)
        if res.status_code != 200:
            logger.error(res.text)


class RouteMatch:
    def __init__(self, text):
        self._text = text

    def match(self, update):
        if update.message.text.strip() != self._text.strip():
            return False

        return True

    def __str__(self):
        return self._text


class RouteChain:
    def __init__(self, next_hop, wait_input=True):
        self.next_hop = next_hop
        self.wait_input = wait_input


def bind_to_command(match):
    def decorator(handler):
        def wrapper(*args, **kwargs):
            handler(*args, **kwargs)

        wrapper._match = match
        return wrapper
    return decorator


class Conversation:
    CONVERSATION_END, CONVERSATION_IN_PROGRESS = range(2)

    def __init__(self, bot):
        self.bot = bot
        self.state = 'entry'

    def change_state(self, state):
        self.state = state

    @classmethod
    def methods_list(cls):
        return [attr_key for attr_key, attr in cls.__dict__.items()
                if isinstance(attr, types.FunctionType)]

    def _handle_one(self, update):
        for attr_key in self.methods_list():
            attr = getattr(self, attr_key)

            route_match = getattr(attr, '_match', None)

            if route_match is None:
                continue

            if route_match.match(update):
                return attr(update)

        handler = getattr(self, self.state)
        return handler(update)

    def handle(self, update):
        result = self._handle_one(update)
        while result is not None:
            self.change_state(result.next_hop.__name__)

            if result.wait_input:
                return self.CONVERSATION_IN_PROGRESS
            result = self._handle_one(update)

        return self.CONVERSATION_END

    def entry(self, update):
        return NotImplemented


class Router:

    def __init__(self, route_map):
        self.route_map = route_map

    @staticmethod
    def _handle_conversation(bot, update, conversation_cls=None):
        if update.route_state['conversation'] is None:
            update.route_state['conversation'] = conversation_cls(bot)

        result = update.route_state['conversation'].handle(update)
        if result == Conversation.CONVERSATION_END:
            update.route_state['conversation'] = None

    def handle(self, bot, update):
        if update.route_state['conversation'] is not None:
            self._handle_conversation(bot, update)
            return

        for key, handler in self.route_map.items():
            if key.match(update):
                if isinstance(handler, types.FunctionType):
                    handler(bot, update)
                elif issubclass(handler, Conversation):
                    self._handle_conversation(bot, update, handler)
