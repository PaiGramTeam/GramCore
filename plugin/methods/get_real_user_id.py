from typing import TYPE_CHECKING

from gram_core.services.channels.services import ChannelAliasService

if TYPE_CHECKING:
    from . import PluginFuncMethods
    from telegram import Update


class GetRealUserId:
    async def get_real_user_id(self: "PluginFuncMethods", update: "Update") -> int:
        message = update.effective_message
        if message:
            channel = message.sender_chat
            if channel:
                channel_alias_service: ChannelAliasService = self.application.managers.services_map.get(
                    ChannelAliasService, None
                )
                if channel_alias_service:
                    if uid := await channel_alias_service.get_uid_by_chat_id(channel.id):
                        return uid
        user = update.effective_user
        return user.id
