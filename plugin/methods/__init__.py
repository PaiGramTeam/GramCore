from .application import ApplicationMethod
from .delete_message import DeleteMessage
from .download_resource import DownloadResource
from .get_args import GetArgs
from .get_chat import GetChat
from .get_real_user_id import GetRealUserId
from .get_real_user_name import GetRealUserName
from .log_user import LogUser
from .migrate_data import MigrateData


class PluginFuncMethods(
    ApplicationMethod,
    DeleteMessage,
    DownloadResource,
    GetArgs,
    GetChat,
    GetRealUserId,
    GetRealUserName,
    LogUser,
    MigrateData,
):
    """插件方法"""
