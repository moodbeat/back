from pydantic import BaseModel, EmailStr, PositiveInt, conint


class NeedHelpPostRequest(BaseModel):
    recipient: PositiveInt
    type: PositiveInt
    comment: str


class ConditionPostRequest(BaseModel):
    mood: conint(ge=1, le=5)


class AuthCodePostRequest(BaseModel):
    email: EmailStr


class AuthTokenPostRequest(BaseModel):
    email: EmailStr
    code: conint(ge=100000, le=999999)
    telegram_id: PositiveInt


class AuthTokenRefreshPostRequest(BaseModel):
    refresh: str
