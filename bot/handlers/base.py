from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from config_reader import config
from handlers.api_request import make_get_request
from middlewares.auth import AuthMiddleware


router = Router()

router.message.middleware(AuthMiddleware())


@router.message(Command('start'))
async def cmd_start(message: types.Message, state: FSMContext):
    state = await state.get_data()
    headers = state.get('headers')
    response = await make_get_request(
        config.base_endpoint + 'users/current_user/',
        headers=headers
    )

    start_msg = (
        f'Приветсвую, '
        f'{response.get("first_name", message.from_user.first_name)}. '
        f'Я умею почти всё, что умеет сервис «Настроение сотрудника»: '
        f'cо мной Вы можете проходить опросы, '
        f'отмечать своё состоянии в течение дня, '
        f'читать полезные новости и статьи, '
        f'получать уведомления о проходящих мероприятиях.\n\n'
        f'Список доступных команд:\n'
        f'/entries - Список доступных событий\n'
        f'/events - Список актуальных мероприятий\n'
        f'/mood - Пройти опрос о своём состоянии\n'
        f'/survey - Список доступных опросов\n'
        f'/need_help - Отправить запрос на личную встречу со специалистом'
    )
    await message.answer(start_msg)
