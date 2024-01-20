from typing import List, Optional

from gram_core.base_service import BaseService
from gram_core.services.groups.cache import GroupBanCache, GroupUpdateCache
from gram_core.services.groups.models import GroupDataBase as Group
from gram_core.services.groups.repositories import GroupRepository

__all__ = ("GroupService",)


class GroupService(BaseService):
    def __init__(self, group_repository: GroupRepository, ban_cache: GroupBanCache, update_cache: GroupUpdateCache):
        self._repository = group_repository
        self._ban_cache = ban_cache
        self._update_cache = update_cache

    async def initialize(self):
        await self._ban_cache.remove_all()
        groups = await self._repository.get_all(is_banned=True)
        for group in groups:
            await self._ban_cache.set(group.chat_id)
        groups = await self._repository.get_no_need_update(limit=0)
        for group in groups:
            await self._update_cache.set(group.chat_id)

    async def get_group_by_id(self, chat_id: int) -> Optional[Group]:
        """从数据库获取群组信息
        :param chat_id:群组ID
        :return: Group
        """
        return await self._repository.get_by_chat_id(chat_id)

    async def remove(self, group: Group):
        await self._update_cache.remove(group.chat_id)
        await self._ban_cache.remove(group.chat_id)
        return await self._repository.remove(group)

    async def update_cache(self, group: Group):
        if group.is_banned:
            await self._ban_cache.set(group.chat_id)
        elif await self._ban_cache.ismember(group.chat_id):
            await self._ban_cache.remove(group.chat_id)

    async def update_group(self, group: Group) -> Group:
        await self.update_cache(group)
        return await self._repository.update(group)

    async def is_banned(self, chat_id: int) -> bool:
        return await self._ban_cache.ismember(chat_id)

    async def del_ban(self, chat_id: int) -> bool:
        group = await self.get_group_by_id(chat_id)
        if group and group.is_banned:
            group.is_banned = False
            await self.update_group(group)
            return True
        return False

    async def get_ban_list(self) -> List[int]:
        return await self._ban_cache.get_all()

    async def is_need_update(self, chat_id: int) -> bool:
        return not (await self._update_cache.is_member(chat_id))

    async def set_update(self, chat_id: int) -> bool:
        return await self._update_cache.set(chat_id)

    async def remove_update(self, chat_id: int) -> bool:
        return await self._update_cache.remove(chat_id)

    async def join(self, chat_id: int) -> bool:
        group = await self.get_group_by_id(chat_id)
        if group and group.is_left:
            group.is_left = False
            await self.update_group(group)
            return True
        return False

    async def leave(self, chat_id: int) -> bool:
        group = await self.get_group_by_id(chat_id)
        if group and not group.is_left:
            group.is_left = True
            await self.update_group(group)
            return True
        return False
