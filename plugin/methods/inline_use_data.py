from dataclasses import dataclass
from typing import Optional, List

from telegram.ext import ContextTypes
from telegram.ext._utils.types import HandlerCallback, UT, CCT, RT


@dataclass
class IInlineUseData:
    """Inline 使用数据"""

    text: str
    hash: str
    callback: HandlerCallback[UT, CCT, RT]
    cookie: bool = False
    player: bool = False
    UID_KEY: str = "inline_uid"

    def is_show(self, has_cookie: bool, has_player: bool) -> bool:
        """是否显示"""
        if self.cookie and not has_cookie:
            return False
        if self.player and not has_player:
            return False
        return True

    def get_button_callback_data(self, start: str) -> str:
        """获取按钮数据"""
        return f"{start}|{self.hash}"

    @staticmethod
    def set_uid_to_context(context: "ContextTypes.DEFAULT_TYPE", uid: int) -> None:
        """设置 UID 到 Update"""
        user_data = context.user_data
        user_data[IInlineUseData.UID_KEY] = uid

    @staticmethod
    def get_uid_from_context(context: "ContextTypes.DEFAULT_TYPE") -> int:
        """从 Update 中获取 UID"""
        user_data = context.user_data
        if not user_data:
            return 0
        return user_data.get(IInlineUseData.UID_KEY, 0)


class InlineUseData:
    async def get_inline_use_data(self) -> List[Optional[IInlineUseData]]:
        """获取 Inline 使用数据"""
        return []
