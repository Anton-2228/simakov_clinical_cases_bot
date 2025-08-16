import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from environments import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB


def create_url() -> str:
    host = POSTGRES_HOST
    assert host is not None, "Set enviroment variable 'POSTGRES_HOST'"

    port = POSTGRES_PORT
    assert port is not None, "Set enviroment variable 'POSTGRES_PORT'"

    user = POSTGRES_USER
    assert user is not None, "Set enviroment variable 'POSTGRES_USER'"

    password = POSTGRES_PASSWORD
    assert password is not None, "Set enviroment variable 'POSTGRES_PASSWORD'"

    db = POSTGRES_DB
    assert db is not None, "Set enviroment variable 'POSTGRES_DB'"

    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"


ENGINE = create_async_engine(url=create_url(), echo=False, pool_size=5, max_overflow=10)
SESSION_FACTORY = async_sessionmaker(ENGINE)


class Base(DeclarativeBase):  # pylint: disable=too-few-public-methods
    pass


async def create_tables():
    async with ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    async with ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
