class ApplicationError(Exception):
    """Кастомное исключение для бизнес-логики приложения."""

    detail: str = 'Неопознанная ошибка. Мы её обязательно исправим!'


class InvalidHotLineMessageError(ApplicationError):
    """Исключение для невалидных сообщений `горячей линии`."""

    detail: str = 'Ваше обращение должно быть от 4 до 496 знаков'


class InvalidUserEmailError(ApplicationError):
    """Исключение для невалидной электронной почты."""

    detail: str = (
        'Введён некорректный адрес электронной почты.\n\n'
        'Попробуйте снова.'
    )


class UserNotFoundError(ApplicationError):
    """Исключение для отсутствующего пользователя в БД."""

    detail: str = 'Пользователь с таким email отсутствует.'
