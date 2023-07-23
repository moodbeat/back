from typing import Any

from aiogram.fsm.context import FSMContext

from .api.request_models import HeadersRequest
from .storage_service import get_object_from_storage, save_object_in_storage


async def get_headers_from_storage(state: FSMContext) -> HeadersRequest | None:
    """Возвращает объект `headers` из хранилища контекстных данных.

    При отсутствии данных возвращает None.
    """
    return await get_object_from_storage(
        key='headers',
        model=HeadersRequest,
        state=state
    )


async def save_headers_in_storage(
    data: dict[str, Any],
    state: FSMContext
) -> None:
    """Сохраняет объект `headers` в хранилище контекстных данных."""
    obj = HeadersRequest(**data)
    await save_object_in_storage(
        key='headers',
        obj=obj,
        state=state
    )
