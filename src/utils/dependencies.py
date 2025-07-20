from fastapi import Request, Response

from src.storage.cookie_storage_manager import CookieStorageManager
from src.http_client.httpx_http_client import HttpxHttpClient


def get_cookie_storage_manager(
        request: Request,
) -> CookieStorageManager:
    return CookieStorageManager(request)

def get_httpx_http_client() -> HttpxHttpClient:
    return HttpxHttpClient()