import asyncio
from typing import TypeVar, Optional, TYPE_CHECKING

from telegram import Update
from telegram.constants import ChatType
from telegram.error import TelegramError
from telegram.ext import ContextTypes, ApplicationHandlerStop, TypeHandler

from gram_core.error import ServiceNotFoundError
from gram_core.services.groups.models import Group
from gram_core.services.groups.services import GroupService

from utils.log import logger

if TYPE_CHECKING:
    from gram_core.application import Application

UT = TypeVar("UT")
CCT = TypeVar("CCT", bound="CallbackContext[Any, Any, Any, Any]")


class GroupHandler(TypeHandler[UT, CCT]):
    _lock = asyncio.Lock()
    __lock = asyncio.Lock()

    def __init__(self, application: "Application"):
        self.application = application
        self.group_service: Optional["GroupService"] = None
        super().__init__(Update, self.group_check_callback)

    async def _group_service(self) -> "GroupService":
        async with self.__lock:
            if self.group_service is not None:
                return self.group_service
            group_service: GroupService = self.application.managers.services_map.get(GroupService, None)
            if group_service is None:
                raise ServiceNotFoundError("GroupService")
            self.group_service = group_service
            return self.group_service

    @staticmethod
    async def exit_group(update: Update):
        try:
            chat_id = update.effective_chat.id
            await update.get_bot().leave_chat(chat_id)
        except TelegramError as e:
            logger.warning("离开群组失败: %s", str(e))

    @staticmethod
    def create_task(coro):
        loop = asyncio.get_event_loop()
        loop.create_task(coro)

    async def update_group(self, update: Update):
        print("update 数据库开始")
        chat_id = update.effective_chat.id
        chat = update.effective_chat
        try:
            chat = await update.get_bot().get_chat(chat_id)
        except TelegramError as e:
            logger.warning("获取群组详细信息失败: %s", str(e))
        new_group = Group.from_chat(chat)
        print("update 获取 tg 成功")
        if group := await self.group_service.get_group_by_id(new_group.chat_id):
            group.type = new_group.type
            group.title = new_group.title
            group.username = new_group.username
            group.updated_at = new_group.updated_at
        else:
            group = new_group
        print("update 获取数据库信息成功")
        await self.group_service.update_group(group)
        print("update 数据库结束")

    async def group_check_callback(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        if update.inline_query is not None:
            return
        if not update.effective_chat:
            return
        chat_id = update.effective_chat.id
        group_service = await self._group_service()
        loop = asyncio.get_event_loop()
        print("update 消息开始")
        async with self._lock:
            if await group_service.is_banned(chat_id):
                self.create_task(self.exit_group(update))
                raise ApplicationHandlerStop
            if update.effective_chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
                return
            if await group_service.is_need_update(chat_id):
                print("update 创建 task 开始")
                self.create_task(self.update_group(update))
                print("update 创建 task 结束")
