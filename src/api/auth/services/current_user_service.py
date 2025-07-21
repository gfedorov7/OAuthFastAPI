from fastapi import Response

from src.api.auth.models import User, RefreshToken
from src.database.base_repository import BaseRepository
from src.exceptions import NotFoundRecordByIdError, UnauthorizeError
from src.http_client.http_client import HttpClient
from src.config import settings


class CurrentUserService:
    def __init__(
            self,
            user_repo: BaseRepository[User],
            token_repo: BaseRepository[RefreshToken],
            http_client: HttpClient,
    ):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.http_client = http_client

        self.url = settings.oauth_settings.google_valid_access_token_url

    async def get_current_user(self, access_token: str) -> User:
        url_with_token = self._generate_url_with_token(access_token)
        payload = await self._get_payload_current_user(url_with_token)

        user_sub = str(payload.get("user_id"))
        user = await self._get_user_by_sub(user_sub)

        token = await self._get_token(user.id)
        self._check_token_to_valid(token, access_token)

        return user

    def _generate_url_with_token(self, access_token: str) -> str:
        return self.url + access_token

    async def _get_payload_current_user(self, url: str) -> dict:
        response = await self.http_client.send_request("GET", url)
        if response.status_code != 200:
            raise UnauthorizeError("Invalid or expired access token")

        return response.json()

    async def _get_user_by_sub(self, user_sub: str) -> User:
        user = await self.user_repo.get_by_conditions(User.user_oauth_id == user_sub)

        if user is None:
            raise NotFoundRecordByIdError(User.__name__, user_sub)

        return user[0]

    async def _get_token(self, user_id: int) -> RefreshToken:
        token = await self.token_repo.get_by_conditions(RefreshToken.user_id == user_id)
        return token[0]

    @staticmethod
    def _check_token_to_valid(token: RefreshToken, access_token: str) -> None:
        if not token or token.access_token != access_token or not token.is_active:
            raise UnauthorizeError("Token is inactive or not found")