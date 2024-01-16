from typing import List, Optional

from gram_core.base_service import BaseService
from gram_core.services.groups.cache import GroupBanCache
from gram_core.services.groups.models import GroupDataBase as Group
from gram_core.services.groups.repositories import GroupRepository

__all__ = "GroupService"


class GroupService(BaseService):
    def __init__(self, group_repository: GroupRepository, cache: GroupBanCache):
        self._repository = group_repository
        self._ban_cache = cache

    async def initialize(self):
        await self._ban_cache.remove_all()
        groups = await self._repository.get_all(is_banned=True)
        for group in groups:
            await self._ban_cache.set(group.chat_id)

    async def get_group_by_id(self, chat_id: int) -> Optional[Group]:
        """从数据库获取群组信息
        :param chat_id:群组ID
        :return: Group
        """
        return await self._repository.get_by_chat_id(chat_id)

    async def remove(self, group: Group):
        return await self._repository.remove(group)

    async def update_cache(self, group: Group):
        if group.is_banned:
            await self._ban_cache.set(group.chat_id)
        elif await self._ban_cache.ismember(group.chat_id):
            await self._ban_cache.remove(group.chat_id)

    async def update_group(self, group: Group):
        await self.update_cache(group)
        return await self._repository.add(group)

    async def is_banned(self, chat_id: int) -> bool:
        return await self._ban_cache.ismember(chat_id)

    async def get_ban_list(self) -> List[int]:
        return await self._ban_cache.get_all()

    async def get_need_update(self, limit: int = 10) -> List[Group]:
        return await self._repository.get_need_update(limit)
