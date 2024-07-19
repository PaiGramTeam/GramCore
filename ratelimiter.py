import asyncio
import contextlib
from typing import Callable, Coroutine, Any, Union, List, Dict, Optional, TypeVar, Type, TYPE_CHECKING, Awaitable

from telegram.error import RetryAfter
from telegram.ext import AIORateLimiter
from telegram.ext._aioratelimiter import null_context

from utils.log import logger

if TYPE_CHECKING:
    from gram_core.application import Application

JSONDict: Type[dict[str, Any]] = Dict[str, Any]
RL_ARGS = TypeVar("RL_ARGS")
T_CalledAPIFunc = Callable[[str, Dict[str, Any], Union[bool, JSONDict, List[JSONDict]]], Awaitable[Any]]


class RateLimiter(AIORateLimiter):
    _lock = asyncio.Lock()
    __slots__ = (
        "_retry_after_event_map",
        "_application",
    )

    def __init__(
        self,
        max_retries: int = 5,
    ) -> None:
        super().__init__(
            max_retries=max_retries,
        )
        self._application: Optional["Application"] = None
        self._retry_after_event_map: Dict[int, asyncio.Event] = {0: asyncio.Event()}
        self._retry_after_event_map[0].set()

    def clear_group_retry_after_event(self, group: Union[str, int]) -> None:
        for key, retry_after_event in self._retry_after_event_map.copy().items():
            if key == group:
                continue
            if retry_after_event.is_set():
                del self._retry_after_event_map[key]

    async def _get_group_retry_after_event(self, group: Union[str, int]) -> asyncio.Event:
        async with self._lock:
            event = self._retry_after_event_map.get(group)
            if event:
                return event
            if isinstance(group, (str, int)):
                if len(self._retry_after_event_map) > 512:
                    self.clear_group_retry_after_event(group)

                if group not in self._retry_after_event_map:
                    event = asyncio.Event()
                    event.set()
                    self._retry_after_event_map[group] = event
                event = self._retry_after_event_map[group]
            if not event:
                event = self._retry_after_event_map[0]
            return event

    async def _run_request(
        self,
        chat: bool,
        group: Union[str, int, bool],
        callback: Callable[..., Coroutine[Any, Any, Union[bool, JSONDict, List[JSONDict]]]],
        args: Any,
        kwargs: Dict[str, Any],
    ) -> Union[bool, JSONDict, List[JSONDict]]:
        base_context = self._base_limiter if (chat and self._base_limiter) else null_context()
        group_context = self._get_group_limiter(group) if group and self._group_max_rate else null_context()

        async with group_context, base_context:
            return await callback(*args, **kwargs)

    async def process_request(
        self,
        callback: Callable[..., Coroutine[Any, Any, Union[bool, JSONDict, List[JSONDict]]]],
        args: Any,
        kwargs: Dict[str, Any],
        endpoint: str,
        data: Dict[str, Any],
        rate_limit_args: Optional[RL_ARGS],
    ) -> Union[bool, JSONDict, List[JSONDict]]:
        max_retries = rate_limit_args or self._max_retries

        group: Union[int, str, bool] = False
        chat: bool = False
        chat_id = data.get("chat_id")
        if chat_id is not None:
            chat = True

        # In case user passes integer chat id as string
        with contextlib.suppress(ValueError, TypeError):
            chat_id = int(chat_id)

        if (isinstance(chat_id, int) and chat_id < 0) or isinstance(chat_id, str):
            # string chat_id only works for channels and supergroups
            # We can't really tell channels from groups though ...
            group = chat_id

        _retry_after_event = await self._get_group_retry_after_event(group)
        await _retry_after_event.wait()

        for i in range(max_retries + 1):
            try:
                result = await self._run_request(chat=chat, group=group, callback=callback, args=args, kwargs=kwargs)
                await self._on_called_api(endpoint, data, result)
                return result
            except RetryAfter as exc:
                if endpoint == "setWebhook" and exc.retry_after == 1:
                    # webhook 已被正确设置
                    return True

                if i == max_retries:
                    logger.warning("chat_id[%s] 达到最大重试限制 max_retries[%s]", chat_id, exc)
                    raise exc

                sleep = exc.retry_after + 0.1
                logger.warning("chat_id[%s] 触发洪水限制 当前被服务器限制 retry_after[%s]秒", chat_id, exc.retry_after)
                # Make sure we don't allow other requests to be processed
                _retry_after_event.clear()
                await asyncio.sleep(sleep)
            finally:
                # Allow other requests to be processed
                _retry_after_event.set()
        return None  # type: ignore[return-value]

    def set_application(self, application: "Application") -> None:
        self._application = application

    async def _on_called_api(
        self,
        endpoint: str,
        data: Dict[str, Any],
        result: Union[bool, JSONDict, List[JSONDict]],
    ) -> None:
        if funcs := [hook(endpoint, data, result) for hook in self._application.get_called_api_funcs()]:
            try:
                await asyncio.gather(*funcs)
            except Exception as e:
                logger.error("Error while running CalledAPI hooks: %s", e)
