from urllib.parse import urljoin

from aiogram.fsm.context import FSMContext

from config_reader import config

from .api.api_request import (get_headers, make_get_request,
                              make_post_request_with_return_data)
from .api.request_models import SurveyResultPostRequest
from .api.response_models import (FullSurveyGetResponse,
                                  ShortSurveyGetResponse,
                                  SurveyResultsAfterPostResponse)
from .storage_service import get_object_from_storage, save_object_in_storage


async def get_last_ten_surveys(
    state: FSMContext
) -> list[ShortSurveyGetResponse] | None:
    headers = await get_headers(state)
    data = await make_get_request(
        urljoin(config.BASE_ENDPOINT, 'metrics/surveys/?limit=10'),
        headers=headers
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
    headers = await get_headers(state)
    data = await make_get_request(
        urljoin(config.BASE_ENDPOINT, f'metrics/surveys/{survey_id}/'),
        headers=headers
    )
    return FullSurveyGetResponse(**data)


async def post_survey_result_data_with_return_data(
    user_data: dict,
    state: FSMContext
) -> SurveyResultsAfterPostResponse:
    data = SurveyResultPostRequest(**user_data)
    headers = await get_headers(state)
    response = await make_post_request_with_return_data(
        urljoin(config.BASE_ENDPOINT, 'metrics/surveys/results/'),
        data=data.dict(),
        headers=headers
    )
    return SurveyResultsAfterPostResponse(**response)


async def get_survey_from_storage(
    state: FSMContext
) -> FullSurveyGetResponse:
    return await get_object_from_storage(
        key='survey',
        model=FullSurveyGetResponse,
        state=state
    )


async def save_survey_in_storage(
    obj: FullSurveyGetResponse,
    state: FSMContext
) -> None:
    await save_object_in_storage(
        key='survey',
        obj=obj,
        state=state
    )
