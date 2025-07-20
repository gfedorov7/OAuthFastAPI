from typing import Type, Sequence, Generic, Dict, Any
import logging

from sqlalchemy import select, func, Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.types import ModelType, ID
from src.exceptions import NotFoundRecordByIdError


logger = logging.getLogger("app.database.base_repository")

class BaseRepository(Generic[ModelType]):
    def __init__(
            self,
            session: AsyncSession,
            model: Type[ModelType],
    ):
        self.session = session
        self.model = model

    async def get_by_id(self, id_: ID) -> ModelType:
        instance = await self._get_by_id(id_)
        self._check_exists_instance(instance, id_)
        return instance

    async def get_all(self, offset: int = 0, limit: int = 10) -> Sequence[ModelType]:
        stmt = select(self.model).offset(offset).limit(limit)
        return await self._get_all_results_from_query(stmt)

    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        instance = self._add_to_session(obj_in)
        await self._commit_and_refresh(instance)
        return instance

    async def update(self, id_: ID, obj_update: Dict[str, Any]) -> ModelType:
        instance = await self.get_by_id(id_)
        instance = self._update_instance(instance, obj_update)
        await self._commit_and_refresh(instance)
        return instance

    async def delete(self, id_: ID) -> None:
        instance = await self.get_by_id(id_)
        await self.session.delete(instance)
        await self.session.commit()

    async def exists(self, *conditions) -> bool:
        stmt = select(self.model).where(*conditions).limit(1)
        instances = await self._get_all_results_from_query(stmt)
        return self._condition_for_check_exists_instances(instances)

    async def count(self, *conditions) -> int:
        stmt = select(func.count()).select_from(self.model).where(*conditions)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() or 0

    async def get_by_conditions(self, *conditions) -> Sequence[ModelType]:
        stmt = select(self.model).where(*conditions)
        return await self._get_all_results_from_query(stmt)

    async def _get_by_id(self, id_: ID) -> ModelType | None:
        stmt = select(self.model).where(self.model.id == id_)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    def _check_exists_instance(self, instance: ModelType | None, id_: ID) -> None:
        if instance is None:
            logger.warning(f"{self.model.__name__} not found with ID {id_}")
            raise NotFoundRecordByIdError(self.model.__name__, id_)

    def _add_to_session(self, obj_in: Dict[str, Any]) -> ModelType:
        instance = self.model(**obj_in)
        self.session.add(instance)
        return instance

    async def _commit_and_refresh(self, instance: ModelType | None) -> None:
        await self.session.commit()
        if instance:
            await self.session.refresh(instance)

    @staticmethod
    def _update_instance(instance: ModelType, obj_update: Dict[str, Any]) -> ModelType:
        for key, value in obj_update.items():
            if value is not None:
                setattr(instance, key, value)
        return instance

    @staticmethod
    def _condition_for_check_exists_instances(instances: Sequence[ModelType]) -> bool:
        return len(instances) != 0

    async def _get_all_results_from_query(self, stmt: Select) -> Sequence[ModelType]:
        result = await self.session.execute(stmt)
        return result.scalars().all()