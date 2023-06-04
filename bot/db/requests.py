from sqlalchemy import select

from .base import async_session_maker
from .models import Auth


async def save_auth_data(telegram_id, email, access_token, refresh_token):
    async with async_session_maker() as session:
        auth = Auth(
            telegram_id=telegram_id,
            email=email,
            access_token=access_token,
            refresh_token=refresh_token
        )
        session.add(auth)
        await session.commit()


async def get_user_by_telegram_id(telegram_id):
    async with async_session_maker() as session:
        query = select(Auth).filter_by(telegram_id=telegram_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
