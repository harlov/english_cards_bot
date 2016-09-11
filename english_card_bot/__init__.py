from telegraph_commander.bot import BaseBot
from telegraph_commander.command import CommandRouter
from telegraph_commander.logger import get_console_handler
from english_card_bot.config import EnglishCardBotConfig

import logging


class EnglishCardBot(BaseBot):
    router_class = CommandRouter
    config_class = EnglishCardBotConfig


bot = EnglishCardBot()
bot.logger.addHandler(get_console_handler())