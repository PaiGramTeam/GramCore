from typing import TYPE_CHECKING, Callable, Union

if TYPE_CHECKING:
    from telegram import Update


class LogUser:
    @staticmethod
    def log_user(update: Union["Update", int], func: Callable, msg: str, *args, **kwargs) -> None:
        start_msg = "用户 %s[%s] "
        if isinstance(update, int):
            args2 = ("", update) + args
            if update < 0:
                start_msg = "频道 %s[%s] "
        else:
            user = update.effective_user
            args2 = (user.full_name, user.id) + args
            message = update.effective_message
            if message:
                channel = message.sender_chat
                if channel:
                    start_msg = "频道 %s[%s] "
                    args2 = (channel.title, channel.id) + args
        func(start_msg + str(msg), *args2, **kwargs)
