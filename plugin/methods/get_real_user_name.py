from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from telegram import Update


class GetRealUserName:
    @staticmethod
    def get_real_user_name(
        update: "Update",
    ) -> str:
        user = update.effective_user
        message = update.effective_message
        if message:
            channel = message.sender_chat
            if channel:
                return channel.title
        return user.first_name
