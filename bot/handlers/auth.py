from http import HTTPStatus

import requests
from aiogram import Router, flags
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from email_validator import EmailNotValidError, validate_email

from config_reader import config
from db.models import Auth
from db.requests import add_auth_data, find_user, update_auth_data

router = Router()


class AuthState(StatesGroup):
    email = State()
    password = State()


@router.message(Command('auth'))
@flags.state_reset
async def auth_email(message: Message, state: FSMContext):
    await message.answer(
        f'Приветсвую, {message.from_user.first_name}! '
        f'Я телеграм-бот сервиса «Настроение сотрудника».\n'
        f'Для идентификации в системе мне необходимо знать Ваш '
        f'адрес электронной почты.'
    )
    await state.set_state(AuthState.email)


@router.message(AuthState.email)
async def auth_password(message: Message, state: FSMContext):
    email = message.text

    try:
        valid_email = validate_email(email, check_deliverability=False)
        email = valid_email.normalized

        await state.update_data(email=email)
        await state.set_state(AuthState.password)
        await message.answer('Введите пароль:')

    except EmailNotValidError:
        await message.answer(
            'Введён некорректный адрес электронной почты.\n\n'
            'Попробуйте снова.'
        )


@router.message(AuthState.password)
async def save_user_data(message: Message, state: FSMContext):
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
            config.BASE_ENDPOINT + 'auth/jwt/create/', json=data
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
            await message.answer('Какие-то проблемы.')

        return  # noqa

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
    await message.answer('Вы успешно авторизованы.')  # noqa


@router.message(AuthState.password)
async def get_refresh_token(message: Message, user: Auth):

    try:
        token = requests.post(
            config.BASE_ENDPOINT + 'auth/jwt/refresh/',
            json={'refresh': user.refresh_token}
        ).json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return await message.answer(
            'Не удалось соединиться с сервером авторизации.'
        )
    return token
