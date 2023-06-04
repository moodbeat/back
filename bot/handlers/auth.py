import requests
from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config_reader import config
from db.requests import save_auth_data

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
    tokens = get_auth_tokens(email, password)

    await save_auth_data(
        telegram_id=telegram_id,
        email=email,
        access_token=tokens.get('access'),
        refresh_token=tokens.get('refresh')
    )
    await message.answer('Вы успешно авторизованы.')


def get_auth_tokens(email, password):
    data = {
        'email': email,
        'password': password
    }

    try:
        response = requests.post(
            config.base_endpoint + 'auth/jwt/create/', json=data
        )
        return response.json()
    except requests.exceptions.RequestException as error:
        return error
