from src.api.auth.schemas import UserCreate
from src.api.auth.utils.decoder import Decoder
from src.api.auth.models import User
from src.database.base_repository import BaseRepository


class UserSaveService:


    def __init__(
            self,
            decoder: Decoder,
            user_repository: BaseRepository[User],
    ):
        self.decoder = decoder
        self.user_repository = user_repository

    async def save_user(self, token: str) -> User:
        payload = self._get_payload(token)
        user = await self._get_exist_user(payload.get("email"))
        if user:
            return user

        new_user = self._fill_user_schema(payload)
        return await self._create_new_user(new_user)

    def _get_payload(self, token: str) -> dict:
        return self.decoder.decode(token)

    async def _get_exist_user(self, email: str) -> User:
        user = await self.user_repository.get_by_conditions(
            User.email == email
        )
        return user[0] if user else None

    @staticmethod
    def _fill_user_schema(payload: dict) -> dict:
        user = UserCreate(
            user_oauth_id=payload.get("sub"),
            email=payload.get("email"),
            full_name=payload.get("name"),
            image=payload.get("picture"),
        )
        return user.model_dump()

    async def _create_new_user(self, user: dict) -> User:
        return await self.user_repository.create(user)