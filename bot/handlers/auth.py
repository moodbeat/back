from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from email_validator import EmailNotValidError, validate_email

from db.requests import add_auth_data, find_user, update_auth_data
from services.auth_service import post_auth_code_response, post_token_create

router = Router()


class AuthState(StatesGroup):
    email = State()
    code = State()


@router.message(Command('auth'))
async def auth_email(message: Message, state: FSMContext):
    await message.answer(
        f'Приветсвую, {message.from_user.first_name}! '
        'Я телеграм-бот сервиса «Настроение сотрудника».\n'
        'Для идентификации в системе введите Ваш адрес электронной почты.'
    )
    await state.set_state(AuthState.email)


@router.message(AuthState.email)
async def auth_code(message: Message, state: FSMContext):
    email = message.text

    try:
        valid_email = validate_email(email, check_deliverability=False)
        email = valid_email.normalized
    except EmailNotValidError:
        await message.answer(
            'Введён некорректный адрес электронной почты.\n\n'
            'Попробуйте снова.'
        )
        return  # noqa

    await state.update_data(email=email)
    await post_auth_code_response(email)
    await state.set_state(AuthState.code)
    await message.answer(
        'На указанный Вами адрес электронной почты отправлен код.\n'
        'Пожалуйста введите его.'
    )


@router.message(AuthState.code)
async def save_user_data(message: Message, state: FSMContext):
    await state.update_data(code=message.text)
    data = await state.get_data()
    await state.clear()

    email = data.pop('email')
    code = data.pop('code')
    telegram_id = message.from_user.id

    tokens = await post_token_create(
        email=email,
        code=code,
        telegram_id=telegram_id
    )

    data = {
        'telegram_id': telegram_id,
        'email': email,
        'access_token': tokens.get('access'),
        'refresh_token': tokens.get('refresh')
    }

    user_exists = await find_user(telegram_id=telegram_id, email=email)
    if user_exists:
        await update_auth_data(user_exists.id, **data)
        return await message.answer('Добро пожаловать, снова.')

    await add_auth_data(**data)
    await message.answer('Вы успешно авторизованы.')  # noqa
