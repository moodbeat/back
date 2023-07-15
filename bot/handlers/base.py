from aiogram import Router, types
from aiogram.filters import Text
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from config_reader import config
from handlers.api_request import make_get_request
from middlewares.auth import AuthMiddleware

router = Router()

router.message.middleware(AuthMiddleware())


@router.callback_query(Text(startswith='back_start'))
@router.message(Command('start'))
async def cmd_start(
    message: types.Message | types.CallbackQuery, state: FSMContext
):
    state = await state.get_data()
    headers = state.get('headers')
    response = await make_get_request(
        config.base_endpoint + 'users/current_user/',
        headers=headers
    )

    start_msg = (
        f'Приветствую Вас, '
        f'{response.get("first_name", message.from_user.first_name)}.\n'
        f'Я умею почти всё, что умеет сервис «Настроение сотрудника»: '
        f'cо мной Вы можете проходить опросы, '
        f'отмечать своё состояние в течение дня, '
        f'читать полезные новости и статьи, '
        f'получать уведомления о проходящих мероприятиях.\n\n'
        f'Доступные команды:\n'
        f'/entries - список статей\n'
        f'/events - список актуальных мероприятий\n'
        f'/mood - отметить своё состояние\n'
        f'/survey - список опросов для прохождения\n'
        f'/need_help - отправить запрос на личную встречу со специалистом'
    )

    if isinstance(message, types.CallbackQuery):
        await message.message.delete()
    else:
        await message.answer(start_msg)
