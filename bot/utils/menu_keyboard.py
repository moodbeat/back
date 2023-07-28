from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def create_menu_keyboard() -> ReplyKeyboardMarkup:
    menu_keyboard: list[KeyboardButton] = [
        [
            KeyboardButton(text='Статьи'),
            KeyboardButton(text='Мероприятия')
        ],
        [
            KeyboardButton(text='Состояние'),
            KeyboardButton(text='Опросы')
        ],
        [
            KeyboardButton(text='Анонимные обращения'),
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=menu_keyboard,
        resize_keyboard=True,
        is_persistent=True
    )
