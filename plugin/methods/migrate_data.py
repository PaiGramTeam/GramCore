from abc import ABC, abstractmethod
from typing import Optional, TypeVar, List, Any, Tuple, Type

T = TypeVar("T")


class IMigrateData(ABC):
    @abstractmethod
    async def migrate_data_msg(self) -> str:
        """返回迁移数据的提示信息"""

    @abstractmethod
    async def migrate_data(self) -> bool:
        """迁移数据"""

    @staticmethod
    def get_sql_data_by_key(model: T, keys: Tuple[Any, ...]) -> tuple[Any, ...]:
        """通过 key 获取数据"""
        data = []
        for i in keys:
            data.append(getattr(model, i.key))
        return tuple(data)

    @staticmethod
    async def filter_sql_data(
        model: Type[T], service_method, old_user_id: int, new_user_id: int, keys: Tuple[Any, ...]
    ) -> List[T]:
        data: List[model] = await service_method(old_user_id)
        if not data:
            return []
        new_data = await service_method(new_user_id)
        new_data_index = [IMigrateData.get_sql_data_by_key(p, keys) for p in new_data]
        need_migrate = []
        for d in data:
            if IMigrateData.get_sql_data_by_key(d, keys) not in new_data_index:
                need_migrate.append(d)
        return need_migrate


class MigrateData:
    async def get_migrate_data(self, old_user_id: int, new_user_id: int) -> Optional[IMigrateData]:
        """获取迁移数据"""
        if not (old_user_id and new_user_id):
            return None
        return None
