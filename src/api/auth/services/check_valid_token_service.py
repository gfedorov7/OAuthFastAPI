from src.api.auth.utils.state_compare import StateCompare
from src.storage.storage_manager import StorageManager
from src.api.auth.services.google_service_mixin import GoogleServiceMixin


class CheckValidTokenService(GoogleServiceMixin):
    def __init__(
        self,
        state_compare: StateCompare,
        storage_manager: StorageManager,
    ):
        super().__init__(storage_manager)
        self.state_compare = state_compare

    def compare_token(self, google_token: str) -> None:
        saved_state = self._get_saved_state()
        self._compare_state(google_token, saved_state)

    def _get_saved_state(self) -> str:
        return self.storage_manager.get_(self.state_token_key)

    def _compare_state(self, google_token: str, saved_state: str) -> None:
        self.state_compare.compare(google_token, saved_state)
