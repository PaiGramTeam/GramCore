from .application import ApplicationMethod
from .delete_message import DeleteMessage
from .download_resource import DownloadResource
from .get_args import GetArgs
from .get_chat import GetChat
from .get_real_uid_or_offset import GetRealUidOrOffset
from .get_real_user_id import GetRealUserId
from .get_real_user_name import GetRealUserName
from .inline_use_data import InlineUseData
from .log_user import LogUser
from .migrate_data import MigrateData


class PluginFuncMethods(
    ApplicationMethod,
    DeleteMessage,
    DownloadResource,
    GetArgs,
    GetChat,
    GetRealUidOrOffset,
    GetRealUserId,
    GetRealUserName,
    InlineUseData,
    LogUser,
    MigrateData,
):
    """插件方法"""
