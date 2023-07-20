from pydantic import BaseModel, PositiveInt, conint


class HotLinePostRequest(BaseModel):
    recipient: PositiveInt
    type: PositiveInt
    comment: str


class ConditionPostRequest(BaseModel):
    mood: conint(ge=1, le=5)


class SurveyResult(BaseModel):
    question_id: PositiveInt
    variant_value: conint(ge=0)


class SurveyResultPostRequest(BaseModel):
    survey: PositiveInt
    results: list[SurveyResult]
