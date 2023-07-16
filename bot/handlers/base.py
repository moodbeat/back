from aiogram import Router, types
from aiogram.filters import Text
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from middlewares.auth import AuthMiddleware
from services.user_service import get_current_user

router = Router()

router.message.middleware(AuthMiddleware())


@router.callback_query(Text(startswith='back_start'))
@router.message(Command('start'))
async def cmd_start(
    message: types.Message | types.CallbackQuery, state: FSMContext
):
    user = await get_current_user(state)

    start_msg = (
        f'Приветствую Вас, {user.first_name}.\n'
        'Я умею почти всё, что умеет сервис «Настроение сотрудника»: '
        'cо мной Вы можете проходить опросы, '
        'отмечать своё состояние в течение дня, '
        'читать полезные новости и статьи, '
        'получать уведомления о проходящих мероприятиях.\n\n'
        'Доступные команды:\n'
        '/entries - список последних статей\n'
        '/events - список актуальных мероприятий\n'
        '/conditions - отметить своё состояние\n'
        '/survey - список опросов для прохождения\n'
        '/need_help - отправить запрос на личную встречу со специалистом'
    )

    if isinstance(message, types.CallbackQuery):
        await message.message.delete()
        await state.set_state(state=None)
    else:
        await message.answer(start_msg)
