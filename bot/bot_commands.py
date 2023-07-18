from aiogram import Bot
from aiogram.types import BotCommand


async def set_bot_commands(bot: Bot):
    """Создаем меню со списком команд."""
    await bot.set_my_commands(
        [
            BotCommand(command='/start', description='Запустить бота'),
            BotCommand(command='/entries', description='Последние статьи'),
            BotCommand(command='/events', description='Доступные мероприятия'),
            BotCommand(command='/conditions', description='Оценка состояния'),
            BotCommand(command='/survey', description='Доступные опросы'),
            BotCommand(command='/need_help', description='Нужна помощь!'),
        ]
    )
