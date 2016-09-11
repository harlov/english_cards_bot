from telegraph_commander.command import BotCommand

from english_card_bot import EnglishCardBot


@EnglishCardBot.router.command('menu')
class MenuCommand(BotCommand):
    async def run(self):
        await self.telegram_api.send_message(self.chat_id, 'not ready menu, sorry)')


@EnglishCardBot.router.command('add')
class AddWordCommand(BotCommand):
    PARAMS = [
        dict(name='word'),
        dict(name='translation')
    ]

    async def run_handle(self):
        await self.telegram_api.send_message(self.chat_id, 'done')
        await self.end_command()
