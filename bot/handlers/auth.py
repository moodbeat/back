from aiogram import Router, flags
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from email_validator import EmailNotValidError, validate_email

from services.api.response_models import AuthTokensPostResponse
from services.api_service import save_headers_in_storage
from services.auth_service import post_auth_code, post_token_create
from services.user_service import (get_current_user,
                                   save_current_user_in_storage,
                                   update_tokens_of_current_user_in_storage)

router = Router()


class AuthState(StatesGroup):
    email = State()
    code = State()


keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Выйти', callback_data='back_auth'
            ),
        ]
    ]
)


@router.callback_query(Text(startswith='back_auth'))
@router.message(Command('auth'))
@flags.state_reset
async def cmd_auth(message: Message | CallbackQuery, state: FSMContext):
    if isinstance(message, CallbackQuery):
        await message.message.delete()
        return

    await message.answer(
        f'Приветствую, {message.from_user.first_name}! '
        'Я телеграм-бот сервиса «Настроение сотрудника».\n'
        'Для идентификации в системе введите Ваш адрес электронной почты.',
        reply_markup=keyboard
    )
    await state.set_state(AuthState.email)


@router.message(AuthState.email)
async def auth_email(message: Message, state: FSMContext):
    email = message.text

    try:
        valid_email = validate_email(email, check_deliverability=False)
        email = valid_email.normalized
    except EmailNotValidError:
        await message.answer(
            'Введён некорректный адрес электронной почты.\n\n'
            'Попробуйте снова.',
            reply_markup=keyboard
        )
        return

    await state.update_data(email=email)
    await post_auth_code(email)
    await state.set_state(AuthState.code)
    await message.answer(
        'На указанный Вами адрес электронной почты отправлен код.\n'
        'Пожалуйста введите его.',
        reply_markup=keyboard
    )


@router.message(AuthState.code)
async def auth_code(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    try:
        code = int(message.text)
    except ValueError:
        await message.answer(
            'Код должен быть целым числом. Повторите ввод',
            reply_markup=keyboard
        )
        return

    data['code'] = code
    data['telegram_id'] = message.from_user.id

    tokens = await post_token_create(data)
    await save_or_update_user_in_storage(message, tokens, state)


async def save_or_update_user_in_storage(
    message: Message,
    tokens: AuthTokensPostResponse,
    state: FSMContext
):
    current_user = await update_tokens_of_current_user_in_storage(
        tokens,
        state
    )
    if current_user:
        await message.answer('Рады снова Вас видеть!')
        return

    headers = {'Authorization': 'Bearer ' + tokens.access}
    await save_headers_in_storage(headers, state)

    current_user = await get_current_user(state)
    current_user.access = tokens.access
    current_user.refresh = tokens.refresh
    await save_current_user_in_storage(current_user, state)
    await message.answer('Вы успешно авторизованы!')
