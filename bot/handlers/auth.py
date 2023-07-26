from aiogram import F, Router, flags
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)

from services.api.response_models import AuthTokensPostResponse
from services.api_service import save_headers_in_storage
from services.auth_service import (check_and_normalize_user_email,
                                   post_auth_code, post_token_create)
from services.user_service import (get_current_user,
                                   save_current_user_in_storage,
                                   update_tokens_of_current_user_in_storage)
from utils.filters import HasUserEmailFilter

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


@router.message(AuthState.email, HasUserEmailFilter())
async def auth_email(message: Message, state: FSMContext, user_email: str):
    email = check_and_normalize_user_email(user_email)

    await state.update_data(email=email)
    await post_auth_code(email)
    await state.set_state(AuthState.code)
    await message.answer(
        'На указанный Вами адрес электронной почты отправлен код.\n'
        'Пожалуйста введите его.',
        reply_markup=keyboard
    )


@router.message(AuthState.email)
async def auth_email_invalid(message: Message):
    await message.answer(
        ('Некорректный ввод!\n'
         'Введите свой адрес электронной почты, '
         'который зарегистрирован в нашем сервисе'),
        reply_markup=keyboard
    )


@router.message(AuthState.code, F.text.regexp(r'^[1-9]{1}[0-9]{5}$'))
async def auth_code(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    data['code'] = message.text
    data['telegram_id'] = message.from_user.id

    tokens = await post_token_create(data)
    await save_or_update_user_in_storage(message, tokens, state)


@router.message(AuthState.code)
async def auth_code_invalid(message: Message):
    await message.answer(
        ('Некорректный ввод!\n'
         'Код должен быть целым шестизначным числом '
         'от 100000 до 999999'),
        reply_markup=keyboard
    )


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
