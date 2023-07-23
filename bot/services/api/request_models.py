from pydantic import BaseModel, EmailStr, Field, PositiveInt, conint


class HotLinePostRequest(BaseModel):
    recipient: PositiveInt
    type: PositiveInt
    comment: str


class ConditionPostRequest(BaseModel):
    mood: conint(ge=1, le=5)


class AuthCodePostRequest(BaseModel):
    email: EmailStr


class AuthTokensRefreshRequest(BaseModel):
    email: EmailStr
    telegram_id: PositiveInt


class AuthTokensPostRequest(AuthTokensRefreshRequest):
    code: conint(ge=100000, le=999999)


class AccessTokenRefreshRequest(BaseModel):
    refresh: str


class SurveyResult(BaseModel):
    question_id: PositiveInt
    variant_value: conint(ge=0)


class SurveyResultPostRequest(BaseModel):
    survey: PositiveInt
    results: list[SurveyResult]


class HeadersRequest(BaseModel):
    authorization: str = Field(alias='Authorization')
