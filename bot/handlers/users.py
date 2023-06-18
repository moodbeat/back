import requests
from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from config_reader import config
from middlewares.auth import AuthMiddleware

router = Router()

router.message.middleware(AuthMiddleware())


@router.message(Command('mood'))
async def cmd_start(message: types.Message, state: FSMContext):
    state = await state.get_data()
    headers = state.get('headers')
    response = requests.get(
        config.base_endpoint + 'users/current_user/', headers=headers
    ).json()
    if response['latest_condition'] is None:
        await message.answer(
            f'Привет {response["first_name"]}!\n\n'
            'Вы еще не оценивали свое настроение. Предлагаем Вам как можно '
            'скорее его оценить. *дальше типа всплывают кнопки*'
        )
    else:
        await message.answer(
            f'Привет {response["first_name"]}!\n\n'
            'Актуальная оценка состояния по 5-ти балльной шкале: '
            f'{response["latest_condition"]["mood"]}'
        )
