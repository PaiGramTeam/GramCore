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
    from telegram import Bot
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
    async def leave_chat(bot: "Bot", chat_id: int) -> bool:
        try:
            return await bot.leave_chat(chat_id)
        except TelegramError as e:
            logger.warning("退出会话失败: %s", str(e))

    @staticmethod
    async def exit_group_job(context: "CallbackContext"):
        job = context.job
        chat_id = job.chat_id
        await GroupHandler.leave_chat(context.bot, chat_id)

    @staticmethod
    async def update_group(bot: "Bot", group_service: "GroupService", chat: "Chat"):
        try:
            chat = await bot.get_chat(chat.id)
        except TelegramError as e:
            logger.warning("获取会话详细信息失败: %s", str(e))
        new_group = Group.from_chat(chat)
        if group := await group_service.get_group_by_id(new_group.chat_id):
            group.type = new_group.type
            group.title = new_group.title
            group.username = new_group.username
            group.updated_at = new_group.updated_at
        else:
            group = new_group
        await group_service.update_group(group)
        logger.success("更新会话信息成功: %s[%s]", group.title, group.chat_id)

    async def update_group_job(self, context: "CallbackContext"):
        assert isinstance(context.job.data, Chat)
        chat: "Chat" = context.job.data
        group_service = await self._group_service()
        await self.update_group(context.bot, group_service, chat)

    async def group_check_callback(self, update: Update, _: ContextTypes.DEFAULT_TYPE):
        if update.inline_query is not None:
            return
        if not update.effective_chat:
            return
        chat = update.effective_chat
        chat_id = chat.id
        group_service = await self._group_service()
        async with self._lock:
            if await group_service.is_banned(chat_id):
                logger.info("会话 %s[%s] 在黑名单中，尝试退出", chat.title, chat_id)
                self.application.job_queue.run_once(
                    callback=self.exit_group_job,
                    when=1,
                    chat_id=chat_id,
                    name=f"{chat_id}|exit_group",
                )
                raise ApplicationHandlerStop
            if update.effective_chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
                return
            if await group_service.is_need_update(chat_id):
                self.application.job_queue.run_once(
                    callback=self.update_group_job,
                    when=1,
                    data=update.effective_chat,
                    name=f"{chat_id}|update_group",
                )
