import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

engine = create_async_engine('sqlite+aiosqlite:///auth.db')

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main():
    await create_table()

asyncio.run(main())
