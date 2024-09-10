from typing import List, Optional

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from gram_core.base_service import BaseService
from gram_core.dependence.database import Database
from gram_core.services.gacha_log_rank.models import GachaLogRank, GachaLogQueryTypeEnum

__all__ = ("GachaLogRankRepository",)


class GachaLogRankRepository(BaseService.Component):
    def __init__(self, database: Database):
        self.engine = database.engine

    async def add(self, rank: GachaLogRank):
        async with AsyncSession(self.engine) as session:
            session.add(rank)
            await session.commit()

    async def update(self, rank: GachaLogRank) -> GachaLogRank:
        async with AsyncSession(self.engine) as session:
            session.add(rank)
            await session.commit()
            await session.refresh(rank)
            return rank

    async def remove(self, rank: GachaLogRank):
        async with AsyncSession(self.engine) as session:
            await session.delete(rank)
            await session.commit()

    async def get_all(self) -> List[GachaLogRank]:
        async with AsyncSession(self.engine) as session:
            statement = select(GachaLogRank)
            results = await session.exec(statement)
            return results.all()

    async def get_all_by_player_ids(self, rank_type: GachaLogQueryTypeEnum, ids: List[int]) -> List[GachaLogRank]:
        async with AsyncSession(self.engine) as session:
            statement = (
                select(GachaLogRank).where(col(GachaLogRank.player_id).in_(ids)).where(GachaLogRank.type == rank_type)
            )
            results = await session.exec(statement)
            return results.all()

    async def get_by_player_id(
        self, player_id: int, rank_type: Optional[GachaLogQueryTypeEnum]
    ) -> Optional[GachaLogRank]:
        async with AsyncSession(self.engine) as session:
            statement = select(GachaLogRank).where(GachaLogRank.player_id == player_id)
            if rank_type:
                statement = statement.where(GachaLogRank.type == rank_type)
            results = await session.exec(statement)
            return results.first()
