import logging

from fastapi import Response, Request

from src.exceptions import InternalServerError
from src.storage.storage_manager import ResponseAwareStorageManager


logger = logging.getLogger("app.storage.cookie_storage_manager")

class CookieStorageManager(ResponseAwareStorageManager):
    def __init__(self, request: Request):
        self.response: Response | None = None
        self.request = request

    def set_response(self, response: Response) -> None:
        self.response = response

    def set_(self, key: str, value: str, **kwargs) -> None:
        self._check_response_to_none()
        self.response.set_cookie(key, value, **kwargs)

    def get_(self, key: str) -> str:
        return self.request.cookies.get(key)

    def delete_(self, key: str) -> None:
        self._check_response_to_none()
        self.response.delete_cookie(key)

    def _check_response_to_none(self):
        if self.response is None:
            logger.warning("attr response is None")
            raise InternalServerError()