from typing import List, Optional

from gram_core.base_service import BaseService
from gram_core.services.gacha_log_rank.cache import GachaLogRankCache
from gram_core.services.gacha_log_rank.models import GachaLogRank, GachaLogTypeEnum, GachaLogQueryTypeEnum
from gram_core.services.gacha_log_rank.repositories import GachaLogRankRepository

__all__ = ("GachaLogRankService",)


class GachaLogRankService(BaseService):
    def __init__(
        self,
        gacha_log_rank_repository: GachaLogRankRepository,
        gacha_log_rank_cache: GachaLogRankCache,
    ):
        self._repository = gacha_log_rank_repository
        self._cache = gacha_log_rank_cache

    async def del_all_cache_by_type(self, rank_type: "GachaLogTypeEnum", query_type: "GachaLogQueryTypeEnum") -> bool:
        return await self._cache.remove_all(rank_type, query_type)

    async def add_cache(
        self, rank_type: "GachaLogTypeEnum", query_type: "GachaLogQueryTypeEnum", player_id: int, score: int
    ) -> bool:
        return await self._cache.add(rank_type, query_type, player_id, score)

    async def get_ranks_cache(
        self, rank_type: "GachaLogTypeEnum", query_type: "GachaLogQueryTypeEnum", limit: int = 20, desc: bool = True
    ):
        """获取排行榜，默认由高到低排序"""
        return await self._cache.get_ranks(rank_type, query_type, limit, desc)

    async def get_ranks_length_cache(self, rank_type: "GachaLogTypeEnum", query_type: "GachaLogQueryTypeEnum"):
        """获取排行榜长度"""
        return await self._cache.get_ranks_length(rank_type, query_type)

    async def get_rank_by_player_id_cache(
        self, rank_type: "GachaLogTypeEnum", query_type: "GachaLogQueryTypeEnum", player_id: int, desc: bool = True
    ):
        """获取玩家在排行榜中的排名，默认由高到低排序"""
        return await self._cache.get_rank_by_player_id(rank_type, query_type, player_id, desc)

    async def update_cache(self, rank: GachaLogRank):
        for type_str in GachaLogQueryTypeEnum:
            type_str: "GachaLogQueryTypeEnum"
            score = getattr(rank, type_str.value)
            if score:
                await self.add_cache(rank.type, type_str, rank.player_id, score)

    async def add(self, rank: GachaLogRank):
        await self.update_cache(rank)
        req = await self._repository.add(rank)
        return req

    async def update(self, rank: GachaLogRank) -> GachaLogRank:
        await self.update_cache(rank)
        req = await self._repository.update(rank)
        return req

    async def get_ranks_by_ids(self, rank_type: "GachaLogTypeEnum", ranks_ids: List[int]) -> List[GachaLogRank]:
        return await self._repository.get_all_by_player_ids(rank_type, ranks_ids)

    async def get_rank_by_user_id(
        self, user_id: int, rank_type: Optional["GachaLogTypeEnum"] = None
    ) -> List[GachaLogRank]:
        return await self._repository.get_by_player_id(user_id, rank_type)
