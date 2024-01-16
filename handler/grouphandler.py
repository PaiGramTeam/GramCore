import asyncio
from typing import TypeVar, Optional, TYPE_CHECKING

from telegram import Update, Chat
from telegram.constants import ChatType
from telegram.error import TelegramError
from telegram.ext import ContextTypes, ApplicationHandlerStop, TypeHandler, CallbackContext

from gram_core.error import ServiceNotFoundError
from gram_core.services.groups.models import GroupDataBase as Group
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
    async def exit_group(context: "CallbackContext"):
        job = context.job
        chat_id = job.chat_id
        try:
            await context.bot.leave_chat(chat_id)
        except TelegramError as e:
            logger.warning("离开群组失败: %s", str(e))

    async def update_group(self, context: "CallbackContext"):
        assert isinstance(context.job.data, Chat)
        chat: "Chat" = context.job.data
        chat_id = chat.id
        try:
            chat = await context.bot.get_chat(chat_id)
        except TelegramError as e:
            logger.warning("获取群组详细信息失败: %s", str(e))
        new_group = Group.from_chat(chat)
        if group := await self.group_service.get_group_by_id(new_group.chat_id):
            group.type = new_group.type
            group.title = new_group.title
            group.username = new_group.username
            group.updated_at = new_group.updated_at
        else:
            group = new_group
        await self.group_service.update_group(group)

    async def group_check_callback(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        if update.inline_query is not None:
            return
        if not update.effective_chat:
            return
        chat_id = update.effective_chat.id
        group_service = await self._group_service()
        async with self._lock:
            if await group_service.is_banned(chat_id):
                self.application.job_queue.run_once(
                    callback=self.exit_group,
                    when=1,
                    chat_id=chat_id,
                    name=f"{chat_id}|exit_group",
                )
                raise ApplicationHandlerStop
            if update.effective_chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
                return
            if await group_service.is_need_update(chat_id):
                self.application.job_queue.run_once(
                    callback=self.update_group,
                    when=1,
                    data=update.effective_chat,
                    name=f"{chat_id}|update_group",
                )
