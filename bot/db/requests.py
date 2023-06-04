from sqlalchemy import insert, select

from .base import async_session_maker
from .models import Auth


async def add_auth_data(telegram_id, email, access_token, refresh_token):
    async with async_session_maker() as session:
        auth = Auth(
            telegram_id=telegram_id,
            email=email,
            access_token=access_token,
            refresh_token=refresh_token
        )
        session.add(auth)
        await session.commit()


async def update_auth_data(**kwargs):
    async with async_session_maker() as session:
        query = insert(Auth.model).values(**kwargs)
        await session.execute(query)
        await session.commit()


async def find_user(**kwargs):
    async with async_session_maker() as session:
        query = select(Auth).filter_by(**kwargs)
        result = await session.execute(query)
        return result.scalar_one_or_none()
