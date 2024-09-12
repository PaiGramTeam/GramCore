from typing import TYPE_CHECKING

from gram_core.base_service import BaseService
from gram_core.dependence.redisdb import RedisDB

__all__ = ("GachaLogRankCache",)

if TYPE_CHECKING:
    from gram_core.services.gacha_log_rank.models import GachaLogTypeEnum, GachaLogQueryTypeEnum


class GachaLogRankCache(BaseService.Component):
    def __init__(self, redis: RedisDB):
        self.client = redis.client
        self.qname = "gacha_log_ranks"

    def get_key(self, rank_type: "GachaLogTypeEnum", query_type: "GachaLogQueryTypeEnum") -> str:
        return f"{self.qname}:{rank_type.value}:{query_type.value}"

    async def remove_all(self, rank_type: "GachaLogTypeEnum", query_type: "GachaLogQueryTypeEnum") -> bool:
        key = self.get_key(rank_type, query_type)
        return await self.client.delete(key)

    async def add(
        self, rank_type: "GachaLogTypeEnum", query_type: "GachaLogQueryTypeEnum", player_id: int, score: int
    ) -> bool:
        key = self.get_key(rank_type, query_type)
        return await self.client.zadd(key, {player_id: score})

    async def get_ranks(
        self, rank_type: "GachaLogTypeEnum", query_type: "GachaLogQueryTypeEnum", limit: int, desc: bool
    ):
        """获取排行榜，默认由高到低排序"""
        key = self.get_key(rank_type, query_type)
        return await self.client.zrange(key, 0, limit - 1, withscores=True, desc=desc)

    async def get_rank_by_player_id(
        self, rank_type: "GachaLogTypeEnum", query_type: "GachaLogQueryTypeEnum", player_id: int, desc: bool
    ):
        """获取玩家在排行榜中的排名，默认由高到低排序"""
        key = self.get_key(rank_type, query_type)
        func = self.client.zrevrank if desc else self.client.zrank
        return await func(key, player_id)
