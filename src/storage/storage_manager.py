from abc import abstractmethod, ABC

from fastapi import Response


class StorageManager(ABC):

    @abstractmethod
    def set_(self, key: str, value: str, **kwargs) -> None:
        ...

    @abstractmethod
    def get_(self, key: str) -> str:
        ...

    @abstractmethod
    def delete_(self, key: str) -> str:
        ...

class ResponseAwareStorageManager(StorageManager, ABC):
    def set_response(self, response: Response) -> None:
        ...