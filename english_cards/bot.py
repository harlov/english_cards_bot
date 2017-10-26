import json
import sys

from english_cards import logic
from english_cards.logger import logger
from english_cards.base_bot import (
    Bot,
    Router,
    RouteMatch,
    RouteChain,
    Conversation,
    bind_to_command
)

TRAIN_QUEST, TRAIN_ANSWER, = range(2)
ADD_WORD_NAME, ADD_WORD_TRANSLATION, ADD_WORD = range(3)

DEFAULT_CONFIG_PATH = '/etc/english_cards.conf'


def get_config(path=None):
    load_path = path or DEFAULT_CONFIG_PATH
    logger.info('load configuration from %s', load_path)
    return json.load(open(load_path))


def start(bot, update):
    update.reply("""
     /add - Add word to dictionary\n/train - Check your knowledge.
    """)


class AddWordConversation(Conversation):
    def entry(self, update):
        return RouteChain(self.prompt_word, wait_input=False)

    @bind_to_command(RouteMatch('/exit'))
    def exit(self, update):
        return

    def prompt_word(self, update):
        update.reply('Enter word')
        return RouteChain(self.input_word)

    def input_word(self, update):
        update.message.chat.storage['name'] = update.message.text
        return RouteChain(self.prompt_translate, wait_input=False)

    def prompt_translate(self, update):
        update.reply('Enter translation for word {}'.format(
            update.message.chat.storage['name'])
        )
        return RouteChain(self.input_translate)

    def input_translate(self, update):
        try:
            logic.add_word(update.message.chat.storage['name'],
                           update.message.text)
        except logic.LogicError as e:
            update.reply(e)
        else:
            update.reply('Added')

        return RouteChain(self.entry, wait_input=False)

    def done(self, update):
        update.reply('Done')


class TrainConversation(Conversation):
    def entry(self, update):
        return RouteChain(self.prompt_quest, wait_input=False)

    @bind_to_command(RouteMatch('/exit'))
    def exit(self, update):
        return

    def prompt_quest(self, update):
        word = logic.get_random_word()
        if word:
            update.message.chat.storage['quest_word'] = word
            update.reply('Translate "{}"'.format(word.name))
            return RouteChain(self.input_answer)
        else:
            update.reply('Add at least one word first!')
            return

    def input_answer(self, update):
        if update.message.chat.storage['quest_word'].translate.strip() == update.message.text.strip():
            update.reply('Correct!')
        else:
            update.reply('Incorrect!')

        return RouteChain(self.prompt_quest, wait_input=False)


def run_bot_loop(config):
    router = Router(
        {
            RouteMatch('/start'): start,
            RouteMatch('/add'): AddWordConversation,
            RouteMatch('/train'): TrainConversation
        }
    )
    bot = Bot(config['telegram_key'], router)
    bot.run()


def run():
    args = sys.argv[1:]
    config_path = args[0] if args else None
    config = get_config(config_path)
    logger.info('starting english cards bot...')
    run_bot_loop(config)


if __name__ == '__main__':
    run()
