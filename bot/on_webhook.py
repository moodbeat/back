import logging

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from aiohttp.web_request import Request

from bot_commands import set_bot_commands
from config_reader import config
from handlers import auth, base, conditions, entries, events, hot_line, surveys

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()

bot = Bot(token=config.TELEGRAM_TOKEN.get_secret_value())
dp = Dispatcher(storage=storage)


async def telegram_webhook(request: Request) -> web.Response:
    secret_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
    if secret_token != config.SECRET_TOKEN:
        raise web.HTTPUnauthorized('Недействителен секретный токен!')

    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot=bot, update=update)
    return web.Response(text="ok")


async def on_startapp(app: web.Application):
    logging.info('Старт приложения!')
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(
        url=config.get_web_hook_url,
        secret_token=config.SECRET_TOKEN
    )
    dp.include_routers(
        auth.router,
        base.router,
        entries.router,
        events.router,
        hot_line.router,
        surveys.router,
        conditions.router,
    )
    await set_bot_commands(bot)


async def on_shutdown(app: web.Application):
    logging.info('Остановка приложения!')

    await bot.delete_webhook()
    await dp.storage.close()
    await bot.session.close()

    logging.info('Приложение остановлено!')


async def app_constructor():
    app = web.Application()
    app.add_routes([web.post('/telegram_webhook/', telegram_webhook)])
    app.on_startup.append(on_startapp)
    app.on_shutdown.append(on_shutdown)
    return app


def main():
    web.run_app(
        app_constructor(),
        host='localhost',
        port=config.WEB_APP_PORT
    )
