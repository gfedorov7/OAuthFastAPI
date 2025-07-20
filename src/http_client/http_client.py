from abc import ABC, abstractmethod


class HttpClient(ABC):
    @abstractmethod
    async def send_request(self, method, url, /, **kwargs): ...