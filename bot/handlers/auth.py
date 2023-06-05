from http import HTTPStatus

import requests
from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config_reader import config
from db.requests import add_auth_data, find_user, update_auth_data

router = Router()


class AuthState(StatesGroup):
    email = State()
    password = State()


@router.message(Command('auth'))
async def auth_email(message: types.Message, state: FSMContext):
    await state.set_state(AuthState.email)
    await message.answer('Введите email:')


@router.message(AuthState.email)
async def auth_password(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await state.set_state(AuthState.password)
    await message.answer('Введите пароль:')


@router.message(AuthState.password)
async def save_user_data(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    await state.clear()

    email = data.pop('email')
    password = data.pop('password')
    telegram_id = message.from_user.id
    data = {
        'email': email,
        'password': password
    }

    user_exists = await find_user(telegram_id=telegram_id, email=email)

    try:
        response = requests.post(
            config.base_endpoint + 'auth/jwt/create/', json=data
        )
        response.raise_for_status()
        tokens = response.json()

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return await message.answer(
            'Не удалось соединиться с сервером авторизации.'
        )

    except requests.exceptions.RequestException:

        if response.status_code == HTTPStatus.UNAUTHORIZED:
            await message.answer(
                'Не найдено учетной записи с указанными данными.'
            )
        else:
            await message.answer('Какие то проблемы.')

        return

    data = {
        'telegram_id': telegram_id,
        'email': email,
        'access_token': tokens.get('access'),
        'refresh_token': tokens.get('refresh')
    }

    if user_exists:
        await update_auth_data(user_exists.id, **data)
        return await message.answer('Добро пожаловать, снова.')

    await add_auth_data(**data)
    await message.answer('Вы успешно авторизованы.')
