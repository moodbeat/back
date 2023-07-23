from urllib.parse import urljoin

from aiogram.fsm.context import FSMContext

from config_reader import config

from .api.api_request import (make_get_request,
                              make_post_request_with_return_data)
from .api.request_models import SurveyResultPostRequest
from .api.response_models import (FullSurveyGetResponse,
                                  ShortSurveyGetResponse,
                                  SurveyResultsAfterPostResponse)
from .api_service import get_headers_from_storage
from .storage_service import get_object_from_storage, save_object_in_storage


async def get_last_ten_surveys(
    state: FSMContext
) -> list[ShortSurveyGetResponse] | None:
    """Выполняет запрос к API и возвращает десять свежих опросов.

    В случае отсутствия опросов возваращает None.
    """
    headers = await get_headers_from_storage(state)
    data = await make_get_request(
        urljoin(config.BASE_ENDPOINT, 'metrics/surveys/?limit=10'),
        headers=headers.dict()
    )
    if data.get('count') == 0:
        return None
    return [
        ShortSurveyGetResponse(**item) for item in data.get('results')
    ]


async def get_survey_by_id(
    survey_id: int,
    state: FSMContext
) -> FullSurveyGetResponse:
    """Выполняет запрос к API и возвращает опрос по id."""
    headers = await get_headers_from_storage(state)
    data = await make_get_request(
        urljoin(config.BASE_ENDPOINT, f'metrics/surveys/{survey_id}/'),
        headers=headers.dict()
    )
    return FullSurveyGetResponse(**data)


async def post_survey_result_data_with_return_data(
    user_data: dict,
    state: FSMContext
) -> SurveyResultsAfterPostResponse:
    """Выполняет POST-запрос к API с результатами опроса.

    Возвращает объект интерпретации результатов.
    """
    data = SurveyResultPostRequest(**user_data)
    headers = await get_headers_from_storage(state)
    response = await make_post_request_with_return_data(
        urljoin(config.BASE_ENDPOINT, 'metrics/surveys/results/'),
        data=data.dict(),
        headers=headers.dict()
    )
    return SurveyResultsAfterPostResponse(**response)


async def get_survey_from_storage(
    state: FSMContext
) -> FullSurveyGetResponse | None:
    """Возвращает объект опроса из хранилища контекстных данных.

    При отсутствии данных вовзаращает None.
    """
    return await get_object_from_storage(
        key='survey',
        model=FullSurveyGetResponse,
        state=state
    )


async def save_survey_in_storage(
    obj: FullSurveyGetResponse,
    state: FSMContext
) -> None:
    """Сохраняет объект опроса в хранилище контекстных данных."""
    await save_object_in_storage(
        key='survey',
        obj=obj,
        state=state
    )
