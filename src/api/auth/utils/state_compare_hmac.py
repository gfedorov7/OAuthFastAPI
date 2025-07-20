import hmac

from src.api.auth.utils.state_compare import StateCompare
from src.api.auth.exceptions import InvalidStateCompare


class StateCompareHmac(StateCompare):
    @staticmethod
    def compare(google_state: str, cookie_state: str) -> None:
        if not hmac.compare_digest(google_state, cookie_state):
            raise InvalidStateCompare()