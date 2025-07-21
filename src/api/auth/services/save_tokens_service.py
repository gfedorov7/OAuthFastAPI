from datetime import datetime, timedelta

from src.api.auth.models import RefreshToken
from src.database.base_repository import BaseRepository
from src.api.auth.schemas import TokenSave


class SaveTokensService:


    def __init__(
            self,
            token_repository: BaseRepository[RefreshToken]
    ):
        self.token_repository = token_repository

    async def save_or_update_token(self, payload: dict, user_id: int):
        tokens = await self.token_repository.get_by_conditions(
            RefreshToken.user_id == user_id,
        )
        token = self._fill_token_schema(payload, user_id)
        if tokens:
            found_token = tokens[0]
            return await self.token_repository.update(found_token.id, token)

        return await self.token_repository.create(token)

    def _fill_token_schema(self, payload: dict, user_id: int) -> dict:
        token = TokenSave(
            access_token=payload.get("access_token"),
            expires_at=self._expires_calculator(payload.get("expires_in")),
            refresh_token=payload.get("refresh_token", None),
            token_type=payload.get("token_type"),
            is_active=True,
            user_id=user_id,
        )
        return token.model_dump()

    @staticmethod
    def _expires_calculator(expires_at: int) -> datetime:
        return timedelta(seconds=expires_at) + datetime.now()