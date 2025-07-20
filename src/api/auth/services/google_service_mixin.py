from src.config import settings
from src.storage.storage_manager import StorageManager


class GoogleServiceMixin:


    def __init__(
            self,
            storage_manager: StorageManager | None = None,
    ):
        self.storage_manager = storage_manager

        self.state_token_key = settings.oauth_settings.state_token_key

        self.location = settings.oauth_settings.url
        self.redirect_endpoint = settings.oauth_settings.endpoint_callback
        self.redirect_uri = self.location + self.redirect_endpoint

        self.client_id = settings.oauth_settings.client_id
