from enum import Enum
from pathlib import Path
from typing import List, Optional, Set

import dotenv
from pydantic import AnyUrl, Field
from pydantic_settings import SettingsConfigDict

from gram_core.basemodel import Settings
from utils.const import PROJECT_ROOT
from utils.typedefs import NaturalNumber

__all__ = ("ApplicationConfig", "config", "JoinGroups")

dotenv.load_dotenv(dotenv_path=dotenv.find_dotenv(usecwd=True))


class JoinGroups(str, Enum):
    NO_ALLOW = "NO_ALLOW"
    ALLOW_AUTH_USER = "ALLOW_AUTH_USER"
    ALLOW_USER = "ALLOW_USER"
    ALLOW_ALL = "ALLOW_ALL"


class DatabaseConfig(Settings):
    driver_name: str = "mysql+asyncmy"
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None

    model_config = SettingsConfigDict(env_prefix="db_")


class InfluxDBConfig(Settings):
    host: Optional[str] = None
    port: Optional[int] = None
    token: Optional[str] = None
    org: Optional[str] = None

    model_config = SettingsConfigDict(env_prefix="influxdb_")


class RedisConfig(Settings):
    host: str = "127.0.0.1"
    port: int = 6379
    database: int = Field(default=0, validation_alias="redis_db")
    password: Optional[str] = None

    model_config = SettingsConfigDict(env_prefix="redis_")


class LoggerConfig(Settings):
    name: str = "PaiGram"
    width: Optional[int] = None
    time_format: str = "[%Y-%m-%d %X]"
    traceback_max_frames: int = 20
    path: Path = PROJECT_ROOT / "logs"
    render_keywords: List[str] = ["BOT"]
    locals_max_length: int = 10
    locals_max_string: int = 80
    locals_max_depth: Optional[NaturalNumber] = None
    filtered_names: List[str] = ["uvicorn"]

    model_config = SettingsConfigDict(env_prefix="logger_")


class MTProtoConfig(Settings):
    api_id: Optional[int] = None
    api_hash: Optional[str] = None


class WebServerConfig(Settings):
    enable: bool = False
    """是否启用WebServer"""

    url: AnyUrl = "http://localhost:8080"
    host: str = "localhost"
    port: int = 8080

    model_config = SettingsConfigDict(env_prefix="web_")


class ErrorConfig(Settings):
    pb_url: str = ""
    pb_sunset: int = 43200
    pb_max_lines: int = 1000
    sentry_dsn: str = ""
    notification_chat_id: Optional[str] = None

    model_config = SettingsConfigDict(env_prefix="error_")


class ReloadConfig(Settings):
    delay: float = 0.25
    dirs: List[str] = []
    include: List[str] = []
    exclude: List[str] = []

    model_config = SettingsConfigDict(env_prefix="reload_")


class NoticeConfig(Settings):
    """bot自称"""

    bot_name: str = "派蒙"
    user_not_found: str = f"{bot_name}没有找到您所绑定的账号信息，请先私聊{bot_name}绑定账号"
    """权限不匹配"""
    user_mismatch: str = "再乱点我叫西风骑士团、千岩军、天领奉行、三十人团和逐影庭了！"
    """拒绝加入群聊"""
    quit_status: str = f"{bot_name}不想进去！不是旅行者的邀请！"

    model_config = SettingsConfigDict(env_prefix="notice_")


class BotConfig(Settings):
    """Bot 基础设置"""

    token: str = ""
    """BOT的token"""
    base_url: str = "https://api.telegram.org/bot"
    """Telegram API URL"""
    base_file_url: str = "https://api.telegram.org/file/bot"
    """Telegram API File URL"""
    official: List[str] = ["PaimonMasterBot", "HonkaiStarRail_ZH_Bot"]
    """PaiGramTeam Bot"""
    is_webhook: bool = False
    """接收更新类型 1 为 webhook 0 为 轮询 pull"""
    webhook_url: str = "http://127.0.0.1:8080/telegram"
    """webhook url"""

    model_config = SettingsConfigDict(env_prefix="bot_")


class ApplicationConfig(Settings):
    debug: bool = False
    """debug 开关"""
    retry: int = 5
    """重试次数"""
    auto_reload: bool = False
    """自动重载"""

    proxy_url: Optional[AnyUrl] = None
    """代理链接"""

    owner: Optional[int] = None

    channels: List[int] = []
    """文章推送群组"""
    channels_helper: Optional[int] = None
    """消息帮助频道"""

    verify_groups: Set[int] = set()
    """启用群验证功能的群组"""
    join_groups: Optional[JoinGroups] = JoinGroups.NO_ALLOW
    """是否允许机器人被邀请到其它群组"""

    timeout: int = 10
    connection_pool_size: int = 256
    read_timeout: Optional[float] = None
    write_timeout: Optional[float] = None
    connect_timeout: Optional[float] = None
    pool_timeout: Optional[float] = None
    update_read_timeout: Optional[float] = None
    update_write_timeout: Optional[float] = None
    update_connect_timeout: Optional[float] = None
    update_pool_timeout: Optional[float] = None

    genshin_ttl: Optional[int] = None

    enka_network_api_agent: str = ""
    pass_challenge_api: str = ""
    pass_challenge_app_key: str = ""
    pass_challenge_user_web: str = ""

    reload: ReloadConfig = ReloadConfig()
    database: DatabaseConfig = DatabaseConfig()
    influxdb: InfluxDBConfig = InfluxDBConfig()
    logger: LoggerConfig = LoggerConfig()
    webserver: WebServerConfig = WebServerConfig()
    redis: RedisConfig = RedisConfig()
    mtproto: MTProtoConfig = MTProtoConfig()
    error: ErrorConfig = ErrorConfig()
    notice: NoticeConfig = NoticeConfig()
    bot: BotConfig = BotConfig()


ApplicationConfig.update_forward_refs()
config = ApplicationConfig()
