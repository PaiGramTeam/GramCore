import datetime

from gram_core.services.history_data.models import HistoryData
from gram_core.services.history_data.repositories import HistoryDataRepository

__all__ = [
    "HistoryDataBaseServices",
]


class HistoryDataBaseServices:
    DATA_TYPE: int = 0

    def __init__(self, task_repository: HistoryDataRepository) -> None:
        self._repository: HistoryDataRepository = task_repository

    async def add(self, data: HistoryData):
        return await self._repository.add(data)

    async def remove(self, data: HistoryData):
        return await self._repository.remove(data)

    async def update(self, data: HistoryData):
        data.time_updated = datetime.datetime.now()
        return await self._repository.update(data)

    async def get_by_id(self, row_id: int):
        return await self._repository.get_by_id(row_id)

    async def get_by_user_id(self, user_id: int):
        return await self._repository.get_by_user_id(user_id, self.DATA_TYPE)

    async def get_by_user_id_data_id(self, user_id: int, data_id: int):
        return await self._repository.get_by_user_id_data_id(user_id, self.DATA_TYPE, data_id)

    async def get_all(self):
        return await self._repository.get_all(self.DATA_TYPE)

    async def get_all_by_user_id(self, user_id: int):
        return await self._repository.get_all_by_user_id(user_id)
