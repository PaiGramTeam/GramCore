from typing import Optional, List

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from gram_core.base_service import BaseService
from gram_core.dependence.database import Database
from gram_core.services.channels.models import ChannelAliasDataBase as ChannelAlias

__all__ = ("ChannelAliasRepository",)


class ChannelAliasRepository(BaseService.Component):
    def __init__(self, database: Database):
        self.engine = database.engine

    async def get_by_chat_id(self, chat_id: int) -> Optional[ChannelAlias]:
        async with AsyncSession(self.engine) as session:
            statement = select(ChannelAlias).where(ChannelAlias.chat_id == chat_id)
            results = await session.exec(statement)
            return results.first()

    async def add(self, channel_alias: ChannelAlias):
        async with AsyncSession(self.engine) as session:
            session.add(channel_alias)
            await session.commit()

    async def update(self, channel_alias: ChannelAlias) -> ChannelAlias:
        async with AsyncSession(self.engine) as session:
            session.add(channel_alias)
            await session.commit()
            await session.refresh(channel_alias)
            return channel_alias

    async def remove(self, channel_alias: ChannelAlias):
        async with AsyncSession(self.engine) as session:
            await session.delete(channel_alias)
            await session.commit()

    async def get_all(self) -> List[ChannelAlias]:
        async with AsyncSession(self.engine) as session:
            statement = select(ChannelAlias)
            results = await session.exec(statement)
            return results.all()
