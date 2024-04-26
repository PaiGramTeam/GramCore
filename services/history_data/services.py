import datetime
from typing import Optional, Dict, Any

from gram_core.base_service import BaseService
from gram_core.services.history_data.models import HistoryData
from gram_core.services.history_data.repositories import HistoryDataRepository

__all__ = [
    "HistoryDataServices",
]


class HistoryDataServices(BaseService):

    def __init__(self, task_repository: HistoryDataRepository) -> None:
        self._repository: HistoryDataRepository = task_repository

    async def add(self, data: HistoryData):
        return await self._repository.add(data)

    async def remove(self, data: HistoryData):
        return await self._repository.remove(data)

    async def update(self, data: HistoryData):
        data.time_updated = datetime.datetime.now()
        return await self._repository.update(data)

    async def get_by_user_id(self, user_id: int, data_type: int):
        return await self._repository.get_by_user_id(user_id, data_type)

    async def get_all(self, data_type: int):
        return await self._repository.get_all(data_type)

    async def get_all_by_user_id(self, user_id: int):
        return await self._repository.get_all_by_user_id(user_id)

    @staticmethod
    def create(user_id: int, data_id: int, data_type: int, data: Optional[Dict[str, Any]] = None):
        return HistoryData(
            user_id=user_id,
            data_id=data_id,
            time_created=datetime.datetime.now(),
            type=data_type,
            data=data,
        )
