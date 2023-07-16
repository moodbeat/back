from pydantic import BaseModel, PositiveInt, conint


class NeedHelpPostRequest(BaseModel):
    recipient: PositiveInt
    type: PositiveInt
    comment: str


class ConditionPostRequest(BaseModel):
    mood: conint(ge=1, le=5)
