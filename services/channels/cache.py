from typing import Optional

from gram_core.base_service import BaseService
from gram_core.dependence.redisdb import RedisDB

__all__ = ("ChannelAliasCache",)


class ChannelAliasCache(BaseService.Component):
    def __init__(self, redis: RedisDB):
        self.client = redis.client
        self.qname = "channels:alias"
        self.ttl = 1 * 60 * 60

    def cache_key(self, key: int) -> str:
        return f"{self.qname}:{key}"

    async def get_data(self, channel_id: int) -> Optional[int]:
        data = await self.client.get(self.cache_key(channel_id))
        if data:
            return int(data.decode())
        return None

    async def set_data(self, channel_id: int, user_id: int):
        ck = self.cache_key(channel_id)
        await self.client.set(ck, user_id, ex=self.ttl)

    async def delete(self, channel_id: int):
        await self.client.delete(self.cache_key(channel_id))
