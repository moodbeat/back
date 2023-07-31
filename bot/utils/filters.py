from typing import Any

from aiogram import html
from aiogram.filters import BaseFilter
from aiogram.types import Message


class HasUserEmailFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool | dict[str, Any]:
        entities = message.entities or []
        found_emails = [
            item.extract_from(message.text) for item in entities
            if item.type == 'email'
        ]
        if found_emails:
            return {'user_email': html.quote(found_emails[0])}
        return False
