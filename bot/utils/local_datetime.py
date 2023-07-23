from datetime import datetime

from config_reader import config


def get_local_datetime_now() -> datetime:
    """Возвращает дату и время.

    Для часового пояса, указанного в настройках. Переменная `TIME_ZON`.
    """
    tz = config.get_timezone
    return datetime.now(tz)


def timetz_converter(*args):
    return get_local_datetime_now().timetuple()
