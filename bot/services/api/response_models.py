from datetime import date, datetime

from pydantic import (BaseModel, EmailStr, HttpUrl, PositiveInt, conint,
                      validator)


class User(BaseModel):
    id: PositiveInt
    email: EmailStr
    first_name: str
    last_name: str
    patronymic: str | None = None
    role: str


class Author(User):
    role: str | None = None
    full_name: str | None

    @validator('full_name', always=True)
    def get_full_name(cls, v, values) -> str:  # noqa
        return f'{values["first_name"]} {values["last_name"]}'


class Employee(Author):
    pass


class ShortEntryGetResponse(BaseModel):
    id: PositiveInt
    title: str


class FullEntryGetResponse(ShortEntryGetResponse):
    entry_url: HttpUrl
    author: Author
    text: str | None = None
    preview_image: HttpUrl
    url: HttpUrl | None = None

    @validator('url', always=True)
    def check_text_and_url(cls, v, values):  # noqa
        if v and values.get('text'):
            raise ValueError('Должно быть что-то одно (текст или ссылка).')
        return v


class ShortEventGetResponse(BaseModel):
    id: PositiveInt
    name: str


class FullEventGetResponse(ShortEventGetResponse):
    text: str
    start_time: datetime
    end_time: datetime
    author: Author


class HelpSpecialistGetResponse(Author):
    email: EmailStr | None = None


class HelpTypeGetResponse(BaseModel):
    id: PositiveInt
    title: str


class ConditionGetResponse(BaseModel):
    id: PositiveInt
    mood: conint(ge=1, le=5)
    date: datetime


class UserConditionGetResponse(User):
    latest_condition: ConditionGetResponse


class AuthTokensPostResponse(BaseModel):
    refresh: str
    access: str


class AccessTokenRefreshResponse(BaseModel):
    access: str


class SurveyQuestion(BaseModel):
    id: PositiveInt
    text: str


class SurveyVariant(BaseModel):
    text: str
    value: conint(ge=0) | None = None


class ShortSurveyGetResponse(BaseModel):
    id: PositiveInt
    title: str


class FullSurveyGetResponse(ShortSurveyGetResponse):
    frequency: conint(ge=0)
    questions_quantity: PositiveInt
    description: str | None = str()
    author: Author
    questions: list[SurveyQuestion]
    variants: list[SurveyVariant]


class MentalState(BaseModel):
    name: str
    description: str | None = None
    message: str
    level: conint(gt=0, le=3)


class SurveyResultsAfterPostResponse(BaseModel):
    employee: Employee
    survey: ShortSurveyGetResponse
    mental_state: MentalState
    completion_date: date
    next_attempt_date: date


class CurrentUserGetResponse(User, AuthTokensPostResponse):
    refresh: str | None = None
    access: str | None = None
