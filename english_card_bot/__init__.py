from telegraph_commander.bot import BaseBot
from telegraph_commander.command import CommandRouter
from english_card_bot.config import EnglishCardBotConfig

import logging


class EnglishCardBot(BaseBot):
    router = CommandRouter()
    config = EnglishCardBotConfig()


def get_console_handler():
    log_stream_handler = logging.StreamHandler()
    log_stream_handler.setLevel(logging.DEBUG)
    formater = logging.Formatter("[%(asctime)s][%(name)s][%(levelname)s] - %(message)s")
    log_stream_handler.setFormatter(formater)
    return log_stream_handler


bot = EnglishCardBot()
bot.logger.addHandler(get_console_handler())