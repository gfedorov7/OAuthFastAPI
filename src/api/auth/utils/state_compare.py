from abc import ABC, abstractmethod


class StateCompare(ABC):
    @staticmethod
    @abstractmethod
    def compare(google_state: str, cookie_state: str) -> None: ...