from abc import ABC
from litestar.plugins import InitPlugin
from litestar.config.app import AppConfig
from litestar.types import ControllerRouterHandler

class BasePlugin(InitPlugin, ABC):
    """
    Abstract plugin.
    Loader should skip it.
    """
    
    @property
    def plugin_name(self) -> str:
        """Return class name."""
        return self.__class__.__name__

    @property
    def controllers(self) -> list[ControllerRouterHandler]:
        """
        List of controllers. 
        Redefine it in ancestor.
        """
        return []

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        """
        Base logic for controller's registration.
        You can redefine it in ancestors with super()).
        """
        if self.controllers:
            app_config.route_handlers.extend(self.controllers)
        
        print(f"🔌 Plugin [{self.plugin_name}] is plug successfully.")
        return app_config
