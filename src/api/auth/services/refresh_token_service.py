from typing import Sequence, Tuple

from google.oauth2.reauth import refresh_grant

from src.api.auth.schemas import UpdateTokenRequest
from src.exceptions import NotFoundRecordByIdError
from src.http_client.httpx_http_client import HttpxHttpClient
from src.config import settings
from src.api.auth.models import RefreshToken, User
from src.database.base_repository import BaseRepository
from src.api.auth.exceptions import NotFoundToken


class RefreshTokenService:
    def __init__(
            self,
            http_client: HttpxHttpClient,
            token_repository: BaseRepository[RefreshToken],
            user_repository: BaseRepository[User],
    ):
        self.http_client = http_client

        self.grant_type = settings.oauth_settings.grant_type_refresh
        self.client_id = settings.oauth_settings.client_id
        self.client_secret = settings.oauth_settings.client_secret
        self.url_to_update = settings.oauth_settings.google_exchange_url

        self.token_repository = token_repository
        self.user_repository = user_repository

    async def update_tokens(self, refresh_token: str) -> Tuple[dict, int]:
        tokens = await self._find_token(refresh_token)
        token = self._get_refresh_token(tokens)

        params = self._fill_update_token_params(token.refresh_token)

        return await self._send_request_to_update(params), token.user_id

    async def _find_token(self, refresh_token: str) -> Sequence[RefreshToken]:
        return await self.token_repository.get_by_conditions(
            RefreshToken.refresh_token == refresh_token,
            RefreshToken.is_active == True,
        )

    @staticmethod
    def _get_refresh_token(tokens: Sequence[RefreshToken]) -> RefreshToken:
        if tokens:
            return tokens[0]
        raise NotFoundToken()

    def _fill_update_token_params(self, refresh_token: str) -> dict:
        params = UpdateTokenRequest(
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=refresh_token,
            grant_type=self.grant_type,
        )
        return params.model_dump()

    async def _send_request_to_update(self, params: dict) -> dict:
        response = await self.http_client.send_request(
            "POST",
            self.url_to_update,
            data=params,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        return response.json()