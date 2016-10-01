from telegraph_commander.config import BotConfig


class EnglishCardBotConfig(BotConfig):
    TELEGRAM_API_KEY = '<telegram bot api key>'
    DB_CONNECTION = 'sqlite://english_cards.db'
    # DB_CONNECTION = 'postgresql://user:password@localhost:5432/english_cards'

