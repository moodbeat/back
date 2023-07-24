from aiogram import Router, flags, types
from aiogram.filters import Text
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from middlewares import AuthMiddleware
from services.user_service import get_current_user

router = Router()

router.message.middleware(AuthMiddleware())
router.callback_query.middleware(AuthMiddleware())


@router.callback_query(Text(startswith='back_start'))
@router.message(Command('start'))
@flags.state_reset
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
        '/hot_line - отправить анонимное обращение руководству компании'
    )

    if isinstance(message, types.CallbackQuery):
        await message.message.delete()
    else:
        await message.answer(start_msg)
