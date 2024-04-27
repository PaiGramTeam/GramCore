from typing import List, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from gram_core.base_service import BaseService
from gram_core.dependence.database import Database
from gram_core.services.history_data.models import HistoryData

__all__ = ("HistoryDataRepository",)


class HistoryDataRepository(BaseService.Component):
    def __init__(self, database: Database):
        self.engine = database.engine

    async def add(self, data: HistoryData):
        async with AsyncSession(self.engine) as session:
            session.add(data)
            await session.commit()

    async def remove(self, data: HistoryData):
        async with AsyncSession(self.engine) as session:
            await session.delete(data)
            await session.commit()

    async def update(self, data: HistoryData) -> HistoryData:
        async with AsyncSession(self.engine) as session:
            session.add(data)
            await session.commit()
            await session.refresh(data)
            return data

    async def get_by_user_id(self, user_id: int, data_type: int) -> List[Optional[HistoryData]]:
        async with AsyncSession(self.engine) as session:
            statement = select(HistoryData).where(HistoryData.user_id == user_id).where(HistoryData.type == data_type)
            results = await session.exec(statement)
            return results.all()

    async def get_by_user_id_data_id(self, user_id: int, data_type: int, data_id: int) -> List[Optional[HistoryData]]:
        async with AsyncSession(self.engine) as session:
            statement = (
                select(HistoryData)
                .where(HistoryData.user_id == user_id)
                .where(HistoryData.type == data_type)
                .where(HistoryData.data_id == data_id)
            )
            results = await session.exec(statement)
            return results.all()

    async def get_all(self, data_type: int) -> List[HistoryData]:
        async with AsyncSession(self.engine) as session:
            query = select(HistoryData).where(HistoryData.type == data_type)
            results = await session.exec(query)
            return results.all()

    async def get_all_by_user_id(self, user_id: int) -> List[HistoryData]:
        async with AsyncSession(self.engine) as session:
            query = select(HistoryData).where(HistoryData.user_id == user_id)
            results = await session.exec(query)
            return results.all()
