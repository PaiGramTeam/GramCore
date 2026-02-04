"""插件"""

import datetime
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, TYPE_CHECKING, Tuple, Type, TypeVar, Union

# noinspection PyProtectedMember
from telegram._utils.types import JSONDict

# noinspection PyProtectedMember
from telegram.ext._utils.types import JobCallback
from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from gram_core.builtins.dispatcher import AbstractDispatcher

__all__ = ["TimeType", "job", "JobData"]

P = ParamSpec("P")
T = TypeVar("T")
R = TypeVar("R")

TimeType = Union[float, datetime.timedelta, datetime.datetime, datetime.time]

_JOB_ATTR_NAME = "_job_data"


@dataclass(init=True)
class JobData:
    name: str
    data: Any
    chat_id: int
    user_id: int
    type: str
    job_kwargs: JSONDict = field(default_factory=dict)
    kwargs: JSONDict = field(default_factory=dict)
    dispatcher: Optional[Type["AbstractDispatcher"]] = None


class _Job:
    kwargs: Dict = {}

    def __init__(
        self,
        name: str = None,
        data: object = None,
        chat_id: int = None,
        user_id: int = None,
        job_kwargs: JSONDict = None,
        *,
        dispatcher: Optional[Type["AbstractDispatcher"]] = None,
        **kwargs,
    ):
        self.name = name
        self.data = data
        self.chat_id = chat_id
        self.user_id = user_id
        self.job_kwargs = {} if job_kwargs is None else job_kwargs
        self.kwargs = kwargs
        if dispatcher is None:
            from gram_core.builtins.dispatcher import JobDispatcher

            dispatcher = JobDispatcher

        self.dispatcher = dispatcher

    @staticmethod
    def direct_child_class(clazz: Type) -> Type:
        if clazz.__base__ == _Job:
            return clazz
        return _Job.direct_child_class(clazz.__base__)

    def __call__(self, func: JobCallback) -> JobCallback:
        direct_class = self.direct_child_class(self.__class__)
        job_type = re.sub(r"([A-Z])", lambda x: "_" + x.group().lower(), direct_class.__name__).lstrip("_")
        data = JobData(
            name=self.name,
            data=self.data,
            chat_id=self.chat_id,
            user_id=self.user_id,
            job_kwargs=self.job_kwargs,
            kwargs=self.kwargs,
            type=job_type,
            dispatcher=self.dispatcher,
        )
        if hasattr(func, _JOB_ATTR_NAME):
            job_datas = getattr(func, _JOB_ATTR_NAME)
            job_datas.append(data)
            setattr(func, _JOB_ATTR_NAME, job_datas)
        else:
            setattr(func, _JOB_ATTR_NAME, [data])
        return func


class _RunOnce(_Job):
    def __init__(
        self,
        when: TimeType,
        data: object = None,
        name: str = None,
        chat_id: int = None,
        user_id: int = None,
        job_kwargs: JSONDict = None,
        *,
        dispatcher: Optional[Type["AbstractDispatcher"]] = None,
    ):
        super().__init__(name, data, chat_id, user_id, job_kwargs, dispatcher=dispatcher, when=when)


class _RunRepeating(_Job):
    def __init__(
        self,
        interval: Union[float, datetime.timedelta],
        first: TimeType = None,
        last: TimeType = None,
        data: object = None,
        name: str = None,
        chat_id: int = None,
        user_id: int = None,
        job_kwargs: JSONDict = None,
        *,
        dispatcher: Optional[Type["AbstractDispatcher"]] = None,
    ):
        super().__init__(
            name, data, chat_id, user_id, job_kwargs, dispatcher=dispatcher, interval=interval, first=first, last=last
        )


class _RunMonthly(_Job):
    def __init__(
        self,
        when: datetime.time,
        day: int,
        data: object = None,
        name: str = None,
        chat_id: int = None,
        user_id: int = None,
        job_kwargs: JSONDict = None,
        *,
        dispatcher: Optional[Type["AbstractDispatcher"]] = None,
    ):
        super().__init__(name, data, chat_id, user_id, job_kwargs, dispatcher=dispatcher, when=when, day=day)


class _RunDaily(_Job):
    def __init__(
        self,
        time: datetime.time,
        days: Tuple[int, ...] = tuple(range(7)),
        data: object = None,
        name: str = None,
        chat_id: int = None,
        user_id: int = None,
        job_kwargs: JSONDict = None,
        *,
        dispatcher: Optional[Type["AbstractDispatcher"]] = None,
    ):
        super().__init__(name, data, chat_id, user_id, job_kwargs, dispatcher=dispatcher, time=time, days=days)


class _RunCustom(_Job):
    def __init__(
        self,
        data: object = None,
        name: str = None,
        chat_id: int = None,
        user_id: int = None,
        job_kwargs: JSONDict = None,
        *,
        dispatcher: Optional[Type["AbstractDispatcher"]] = None,
    ):
        super().__init__(name, data, chat_id, user_id, job_kwargs, dispatcher=dispatcher)


class _RunCron(_RunCustom):
    def __init__(
        self,
        cron: str = None,
        data: object = None,
        name: str = None,
        chat_id: int = None,
        user_id: int = None,
        job_kwargs: JSONDict = None,
        *,
        dispatcher: Optional[Type["AbstractDispatcher"]] = None,
    ):
        job_kwargs = job_kwargs or {}
        if cron:
            from apscheduler.triggers.cron import CronTrigger

            cron_trigger = CronTrigger.from_crontab(cron)
            job_kwargs.update({"trigger": cron_trigger})
        super().__init__(data, name, chat_id, user_id, job_kwargs, dispatcher=dispatcher)


# noinspection PyPep8Naming
class job:
    run_once = _RunOnce
    run_repeating = _RunRepeating
    run_monthly = _RunMonthly
    run_daily = _RunDaily
    run_custom = _RunCustom
    run_cron = _RunCron
