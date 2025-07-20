from urllib.parse import urlencode

from fastapi.responses import RedirectResponse, Response

from src.api.auth.utils.state_generator import StateGenerator
from src.storage.cookie_storage_manager import CookieStorageManager
from src.storage.storage_manager import StorageManager
from src.config import settings
from src.api.auth.schemas import LoginParams
from src.api.auth.services.google_service_mixin import GoogleServiceMixin


class GoogleLoginService(GoogleServiceMixin):
    def __init__(
            self,
            storage_manager: StorageManager,
            state_generator: StateGenerator,
    ):
        super().__init__(storage_manager)
        self.state_generator = state_generator

        self.google_auth_url = settings.oauth_settings.google_auth_url
        self.state: str | None = None

    def generate_response(self) -> Response:
        self.state = self._generate_state()

        params = self._generate_params_for_login()

        oauth_url = self.google_auth_url + urlencode(params)
        response =  RedirectResponse(oauth_url)

        return response

    def set_response_to_storage(self, response: Response) -> None:
        if isinstance(self.storage_manager, CookieStorageManager):
            self.storage_manager.set_response(response)

    def save_state(self) -> None:
        self.storage_manager.set_(
            self.state_token_key,
            self.state,
            httponly=True,
            secure=True,
            path="/"
        )

    def _generate_state(self) -> str:
        return self.state_generator.generate()

    def _generate_params_for_login(self) -> dict[str, str]:
        params = LoginParams(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            state=self.state
        )
        return params.model_dump()