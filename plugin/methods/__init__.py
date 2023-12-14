from .application import ApplicationMethod
from .delete_message import DeleteMessage
from .download_resource import DownloadResource
from .get_args import GetArgs
from .get_chat import GetChat


class PluginFuncMethods(
    ApplicationMethod,
    DeleteMessage,
    DownloadResource,
    GetArgs,
    GetChat,
):
    """插件方法"""
