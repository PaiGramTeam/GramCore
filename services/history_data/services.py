import contextlib
import datetime
from typing import List

from sqlalchemy.orm.exc import StaleDataError

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

    @staticmethod
    def exists_data(data: HistoryData, old_data: List[HistoryData]) -> bool:
        return False

    async def remove_same_data_by_data(self, data_list: List[HistoryData]) -> int:
        data_list_len = len(data_list)
        need_delete = []
        for i in range(data_list_len):
            new_data = data_list[i]
            for j in range(i + 1, data_list_len):
                old_data = data_list[j]
                if self.exists_data(new_data, [old_data]):
                    need_delete.append(old_data)
        if need_delete:
            await self.try_delete(need_delete)
        return len(need_delete)

    async def try_delete(self, data_list: List[HistoryData]):
        for data in data_list:
            with contextlib.suppress(StaleDataError):
                await self.remove(data)

    async def remove_same_data_by_user(self, user_id: int) -> int:
        all_data = await self.get_all_by_user_id(user_id)
        # group by data_id
        all_data_map = {}
        for data in all_data:
            if data.data_id not in all_data_map:
                all_data_map[data.data_id] = []
            all_data_map[data.data_id].append(data)
        num = 0
        for _, data_list in all_data_map.items():
            if len(data_list) > 1:
                num += await self.remove_same_data_by_data(data_list)
        return num

    async def remove_same_data(self) -> int:
        all_data = await self.get_all()
        user_ids = list(set([i.user_id for i in all_data]))
        num = 0
        for user_id in user_ids:
            num += await self.remove_same_data_by_user(user_id)
        return num
