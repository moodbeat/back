from typing import Type

from aiogram.fsm.context import FSMContext
from pydantic import BaseModel


async def save_object_in_storage(
    key: str,
    obj: Type[BaseModel],
    state: FSMContext
) -> None:
    await state.update_data({key: obj.dict()})


async def get_object_from_storage(
    key: str,
    model: Type[BaseModel],
    state: FSMContext
) -> Type[BaseModel]:
    user_data = await state.get_data()
    return model(**user_data[key])
