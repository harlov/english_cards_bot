from telegraph_commander.command import BotCommand

from english_card_bot import EnglishCardBot
from english_card_bot.db import session, UserDictionary, TelegramUser


@EnglishCardBot.router.command('menu')
class MenuCommand(BotCommand):
    async def run(self):
        await self.telegram_api.send_message(self.chat_id, 'Select action', variants=[['/add', '/check']])


@EnglishCardBot.router.command('add')
class AddWordCommand(BotCommand):
    PARAMS = [
        dict(name='word'),
        dict(name='translation')
    ]

    def add_word(self):
        telegram_user = TelegramUser.get_telegram_user(self.chat_id)
        user_dictionary_record = UserDictionary(word=self.word, translation=self.translation, user=telegram_user)
        session.add(user_dictionary_record)
        session.commit()

    async def run_handle(self):
        self.add_word()
        await self.telegram_api.send_message(self.chat_id, 'done')
        await self.end_command()


@EnglishCardBot.router.command('check')
class CheckOneWord(BotCommand):
    PARAMS = [
        dict(name='translation', dynamic=True)
    ]

    async def run_handle(self):
        user = TelegramUser.get_telegram_user(self.chat_id)
        if self.context.get('right_answer') is None:
            dict_record = UserDictionary.get_random_word(user)
            self.context['right_answer'] = dict_record.translation
            await self.set_state('wait_answer')
            await self.telegram_api.send_message(self.chat_id, 'Enter translation for "{}"'.format(dict_record.word))
            return

        if self.translation == self.context['right_answer']:
            await self.telegram_api.send_message(self.chat_id, 'right!')
        else:
            await self.telegram_api.send_message(self.chat_id, 'wrong!')

        await self.end_command()
        return dict(command='check')