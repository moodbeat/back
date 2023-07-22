import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.redis import RedisStorage
from aiohttp import web
from aiohttp.web_request import Request
from redis.asyncio.client import Redis

from bot_commands import set_bot_commands
from config_reader import config
from handlers import auth, base, conditions, entries, events, hot_line, surveys

logging.basicConfig(level=logging.INFO)
storage = RedisStorage(
    redis=Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=3
    )
)
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


# @dp.errors()
async def errors_handler(err_event: types.ErrorEvent) -> bool:
    logging.error(
        f'Ошибка при обработке запроса {err_event.update.update_id}: '
        f'{err_event.exception}'
    )
    text = 'Извините, что-то пошло не так!'
    if err_event.update.message:
        await err_event.update.message.answer(text)
    elif err_event.update.callback_query:
        await err_event.update.callback_query.message.answer(text)
    return True


@dp.startup()
async def on_startapp(app: web.Application | None = None) -> None:
    logging.info('Старт приложения!')
    await bot.delete_webhook(drop_pending_updates=True)
    if config.WEB_HOOK_MODE:
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


@dp.shutdown()
async def on_shutdown(app: web.Application | None = None) -> None:
    logging.info('Остановка приложения!')

    await bot.delete_webhook()
    await dp.storage.close()
    await bot.session.close()

    logging.info('Приложение остановлено!')


async def app_constructor() -> web.Application:
    app = web.Application()
    app.add_routes([web.post('/telegram_webhook/', telegram_webhook)])
    app.on_startup.append(on_startapp)
    app.on_shutdown.append(on_shutdown)
    return app


if __name__ == '__main__':
    if config.WEB_HOOK_MODE:
        web.run_app(
            app_constructor(),
            host='localhost',
            port=config.WEB_APP_PORT
        )
    else:
        asyncio.run(dp.start_polling(bot))
