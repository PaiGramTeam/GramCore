from typing import List

from gram_core.base_service import BaseService
from gram_core.dependence.redisdb import RedisDB

__all__ = ("GroupBanCache", "GroupUpdateCache", )


class GroupBanCache(BaseService.Component):
    def __init__(self, redis: RedisDB):
        self.client = redis.client
        self.qname = "groups:ban"

    async def ismember(self, chat_id: int) -> bool:
        return await self.client.sismember(self.qname, chat_id)

    async def get_all(self) -> List[int]:
        return [int(str_data) for str_data in await self.client.smembers(self.qname)]

    async def set(self, chat_id: int) -> bool:
        return await self.client.sadd(self.qname, chat_id)

    async def remove(self, chat_id: int) -> bool:
        return await self.client.srem(self.qname, chat_id)

    async def remove_all(self) -> bool:
        return await self.client.delete(self.qname)


class GroupUpdateCache(BaseService.Component):
    def __init__(self, redis: RedisDB):
        self.client = redis.client
        self.qname = "groups:update"
        self.expire = 24 * 60 * 60  # 24h

    def get_key(self, chat_id: int) -> str:
        return f"{self.qname}:{chat_id}"

    async def set(self, chat_id: int) -> bool:
        key = self.get_key(chat_id)
        return await self.client.set(key, 1, ex=self.expire)

    async def remove(self, chat_id: int) -> bool:
        key = self.get_key(chat_id)
        return await self.client.delete(key)

    async def is_member(self, chat_id: int) -> bool:
        key = self.get_key(chat_id)
        return await self.client.exists(key)
