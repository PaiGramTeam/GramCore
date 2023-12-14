from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from gram_core.application import Application


class ApplicationMethod:
    _application: "Optional[Application]" = None

    def set_application(self, application: "Application") -> None:
        self._application = application

    @property
    def application(self) -> "Application":
        if self._application is None:
            raise RuntimeError("No application was set for this PluginManager.")
        return self._application
