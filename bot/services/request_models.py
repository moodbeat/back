from pydantic import BaseModel


class NeedHelpPostRequest(BaseModel):
    recipient: int
    type: int
    comment: str
