from typing import TypeVar

from sqlalchemy.orm import Mapped

from src.database.base import Base


ModelType = TypeVar("ModelType", bound=Base)
ID = TypeVar("ID", int, Mapped[int], str)