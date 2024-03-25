import asyncio
from typing import TypeVar, TYPE_CHECKING, Any, Callable, Awaitable, Union

from telegram import Update
from telegram.ext import ApplicationHandlerStop, BaseHandler

from utils.log import logger

if TYPE_CHECKING:
    from gram_core.application import Application
    from gram_core.plugin._handler import HandlerData, ConversationData
    from telegram.ext import Application as TelegramApplication

RT = TypeVar("RT")
UT = TypeVar("UT")

CCT = TypeVar("CCT", bound="CallbackContext[Any, Any, Any, Any]")
T_PreprocessorsFunc = Callable[
    ["UT", "TelegramApplication[Any, CCT, Any, Any, Any, Any]", Any, "CCT", Union["HandlerData", "ConversationData"]],
    Awaitable[Any],
]


class HookHandler(BaseHandler[Update, CCT]):

    def __init__(
        self,
        handler: BaseHandler[Update, CCT],
        handler_data: Union["HandlerData", "ConversationData"],
        application: "Application",
    ) -> None:
        self.handler = handler
        self.handler_data = handler_data
        self.application = application
        super().__init__(self.handler.callback, self.handler.block)

    def check_update(self, update: object) -> bool:
        if not isinstance(update, Update):
            return False
        return self.handler.check_update(update)

    async def run_preprocessors(
        self,
        update: "UT",
        application: "TelegramApplication[Any, CCT, Any, Any, Any, Any]",
        check_result: Any,
        context: "CCT",
    ) -> bool:
        processors = self.application.get_preprocessors_funcs()
        if not processors:
            return True
        try:
            await asyncio.gather(
                *(processor(update, application, check_result, context, self.handler_data) for processor in processors)
            )
        except ApplicationHandlerStop:
            logger.info("命令预处理器拦截了一条消息")
            return False
        except Exception as e:
            logger.error("Error while running RunPreProcessors hooks: %s", e)
            return True
        return True

    async def handle_update(
        self,
        update: "UT",
        application: "TelegramApplication[Any, CCT, Any, Any, Any, Any]",
        check_result: Any,
        context: "CCT",
    ) -> RT:
        if not await self.run_preprocessors(update, application, check_result, context):
            raise ApplicationHandlerStop
        return await self.handler.handle_update(update, application, check_result, context)
