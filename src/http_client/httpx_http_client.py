import logging

import httpx

from src.exceptions import InternalServerError
from src.http_client.http_client import HttpClient


logger = logging.getLogger("app.http_client.httpx_http_client")

class BaseRequestHttpxClient:
    async def _send_request(self, method, url, *args, **kwargs) -> httpx.Response:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=30.0)) as client:
            request = client.build_request(method, url, *args, **kwargs)
            response = await client.send(request)
            return response

class GetHttpxClient(BaseRequestHttpxClient):
    async def send_request(self, url, headers: dict | None = None) -> httpx.Response:
        return await super()._send_request("GET", url, headers=headers)

class PostHttpxClient(BaseRequestHttpxClient):
    async def send_request(
            self, url, data: dict | None = None, json: dict | None = None, headers: dict | None = None
    ) -> httpx.Response:
        return await super()._send_request("POST", url, data=data, json=json, headers=headers)

class HttpxHttpClient(HttpClient):
    async def send_request(self, method, url, /, **kwargs) -> httpx.Response:
        match method.lower():
            case 'get':
                client = GetHttpxClient()
            case 'post':
                client = PostHttpxClient()
            case _:
                logger.warning(f"Method {method} not supported")
                raise InternalServerError()

        return await client.send_request(url, **kwargs)