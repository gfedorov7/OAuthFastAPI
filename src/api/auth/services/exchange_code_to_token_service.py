from src.api.auth.services.google_service_mixin import GoogleServiceMixin
from src.http_client.http_client import HttpClient
from src.config import settings
from src.api.auth.schemas import ExchangeCode
from src.storage.storage_manager import StorageManager


class ExchangeCodeToTokenService(GoogleServiceMixin):


    def __init__(
            self,
            http_client: HttpClient,
    ):
        super().__init__()
        self.http_client = http_client

        self.client_secret = settings.oauth_settings.client_secret
        self.grant_type = settings.oauth_settings.grant_type

        self.google_exchange_url = settings.oauth_settings.google_exchange_url

    async def get_tokens(self, code: str) -> dict:
        params = self._fill_exchange_code_params(code)

        return await self._request_to_google(params)

    def _fill_exchange_code_params(self, code: str):
        exchange_code_params = ExchangeCode(
            code=code,
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            grant_type=self.grant_type,
        )
        return exchange_code_params.model_dump()

    async def _request_to_google(self, params: dict[str, str]) -> dict:
        response = await self.http_client.send_request(
            "POST",
            self.google_exchange_url,
            data=params,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json()