from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base_repository import BaseRepository
from src.api.auth.models import User, RefreshToken
from src.database.database_helper import database_helper


def get_user_repository(
        session: AsyncSession = Depends(database_helper.session_depends),
) -> BaseRepository[User]:
    return BaseRepository(session, User)

def get_refresh_token_repository(
        session: AsyncSession = Depends(database_helper.session_depends),
) -> BaseRepository[RefreshToken]:
    return BaseRepository(session, RefreshToken)