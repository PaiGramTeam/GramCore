from abc import ABC, abstractmethod
from typing import Optional


class IMigrateData(ABC):
    @abstractmethod
    async def migrate_data_msg(self) -> str:
        """返回迁移数据的提示信息"""

    @abstractmethod
    async def migrate_data(self) -> bool:
        """迁移数据"""


class MigrateData:
    async def get_migrate_data(self, old_user_id: int, new_user_id: int) -> Optional[IMigrateData]:
        """获取迁移数据"""
        if not (old_user_id and new_user_id):
            return None
        return None
