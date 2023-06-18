from sqlalchemy import desc, select, update

from .base import async_session_maker
from .models import Auth


async def add_auth_data(**kwargs):
    async with async_session_maker() as session:
        auth = Auth(**kwargs)
        session.add(auth)
        await session.commit()


async def update_auth_data(id: int, **kwargs):
    async with async_session_maker() as session:
        query = update(Auth).where(Auth.id == id).values(**kwargs)
        await session.execute(query)
        await session.commit()


async def find_user(**kwargs):
    async with async_session_maker() as session:
        query = (
            select(Auth)
            .filter_by(**kwargs)
            .order_by(desc(Auth.auth_date))
            .limit(1)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()
