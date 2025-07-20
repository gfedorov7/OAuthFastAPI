from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    async_sessionmaker, create_async_engine, AsyncSession
)

from src.config import settings


class DatabaseHelper:
    AUTOFLUSH = False
    AUTOCOMMIT = False
    EXPIRE_ON_COMMIT = False

    def __init__(self, url: str, *, echo: bool):
        self.engine = create_async_engine(url, echo=echo)

        self.session_maker = async_sessionmaker(
            bind=self.engine,
            autocommit=self.AUTOCOMMIT,
            autoflush=self.AUTOFLUSH,
            expire_on_commit=self.EXPIRE_ON_COMMIT,
        )

    async def session_depends(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_maker() as session:
            yield session

database_helper = DatabaseHelper(
    settings.database_settings.database_url,
    echo=settings.database_settings.database_echo
)