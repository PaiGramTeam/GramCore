from typing import Optional

from gram_core.base_service import BaseService
from gram_core.services.channels.cache import ChannelAliasCache
from gram_core.services.channels.models import ChannelAliasDataBase as ChannelAlias
from gram_core.services.channels.repositories import ChannelAliasRepository

__all__ = ("ChannelAliasService",)


class ChannelAliasService(BaseService):
    def __init__(self, channel_alias_repository: ChannelAliasRepository, cache: ChannelAliasCache):
        self.channel_alias_repository = channel_alias_repository
        self._cache = cache

    async def initialize(self):
        channels = await self.channel_alias_repository.get_all()
        for channel in channels:
            if channel.chat_id and channel.user_id:
                await self._cache.set_data(channel.chat_id, channel.user_id)

    async def get_by_chat_id(self, chat_id: int) -> Optional[ChannelAlias]:
        return await self.channel_alias_repository.get_by_chat_id(chat_id)

    async def get_uid_by_chat_id(self, chat_id: int) -> Optional[int]:
        if uid := await self._cache.get_data(chat_id):
            return uid
        if channel := await self.get_by_chat_id(chat_id):
            await self._cache.set_data(channel.chat_id, channel.user_id)
            return channel.user_id
        await self._cache.set_data(chat_id, 0)
        return None

    async def add_channel_alias(self, channel_alias: ChannelAlias):
        await self.channel_alias_repository.add(channel_alias)
        await self._cache.set_data(channel_alias.chat_id, channel_alias.user_id)

    async def update_channel_alias(self, channel_alias: ChannelAlias) -> ChannelAlias:
        channel_alias = await self.channel_alias_repository.update(channel_alias)
        await self._cache.set_data(channel_alias.chat_id, channel_alias.user_id)
        return channel_alias

    async def remove_channel_alias(self, channel_alias: ChannelAlias):
        await self.channel_alias_repository.remove(channel_alias)
        await self._cache.delete(channel_alias.chat_id)
