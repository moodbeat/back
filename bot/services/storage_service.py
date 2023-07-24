from typing import Type

from aiogram.fsm.context import FSMContext
from pydantic import BaseModel


async def save_object_in_storage(
    key: str,
    obj: Type[BaseModel],
    state: FSMContext
) -> None:
    """Сохраняет полученный объект в хранилище контекстных данных."""
    await state.update_data({key: obj.dict(by_alias=True)})


async def get_object_from_storage(
    key: str,
    model: Type[BaseModel],
    state: FSMContext
) -> Type[BaseModel] | None:
    """Возвращает запрошенный по ключу объект из хранилища данных.

    При отсутствии данных возвращает None.
    """
    user_data = await state.get_data()
    if user_data.get(key):  # noqa
        return model(**user_data[key])
