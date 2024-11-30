import enum
from pydantic_settings import BaseSettings, SettingsConfigDict

try:
    import ujson as jsonlib
except ImportError:
    import json as jsonlib

__all__ = ("RegionEnum", "Settings", "SettingsConfigDict")


class RegionEnum(int, enum.Enum):
    """账号数据所在服务器"""

    NULL = 0
    HYPERION = 1  # 米忽悠国服 hyperion
    HOYOLAB = 2  # 米忽悠国际服 hoyolab


class Settings(BaseSettings):
    def __new__(cls, *args, **kwargs):
        cls.model_rebuild()
        return super(Settings, cls).__new__(cls)  # pylint: disable=E1120
