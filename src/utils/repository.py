from abc import ABC, abstractmethod

from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one():
        raise NotImplementedError

    @abstractmethod
    async def find_all():
        raise NotImplementedError


class AsyncSQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_one(self, data: dict) -> int:
        stmt = insert(self.model).values(**data)
        res = await self._session.execute(stmt)
        await self._session.commit()
        return res.inserted_primary_key

    async def edit_one(self, id: int, data: dict) -> int:
        stmt = (
            update(self.model).values(**data).filter_by(id=id).returning(self.model.id)
        )
        res = await self._session.execute(stmt)
        return res.scalar_one()

    async def delete_one(self, id: str):
        stmt = delete(self.model).where(getattr(self.model, "id") == id).returning(1)
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def find_all(self, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        res = await self._session.execute(stmt)
        res = [row[0].to_read_model() for row in res.unique().all()]
        return res

    async def find_one(self, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def find_first(self, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        res = await self._session.execute(stmt)
        res = res.scalars()
        res = res.first()
        return res.to_read_model() if res else res
