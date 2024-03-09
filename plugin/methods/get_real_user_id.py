from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import PluginFuncMethods
    from telegram import Update


# TODO: for test
channel_map = {}


class GetRealUserId:
    async def get_real_user_id(
        self: "PluginFuncMethods",
        update: "Update"
    ) -> int:
        message = update.effective_message
        if message:
            channel = message.sender_chat
            if channel:
                return channel_map.get(channel.id, channel.id)
        user = update.effective_user
        return user.id
