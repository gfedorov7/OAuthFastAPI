from typing import TypeVar, Generic, List

from pydantic import BaseModel


T = TypeVar('T')

class PaginationModel(BaseModel, Generic[T]):
    items: List[T]
    total: int