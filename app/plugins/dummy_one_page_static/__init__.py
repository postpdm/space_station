from litestar.plugins import InitPlugin
from litestar.config.app import AppConfig

from .controller import Dummy_One_Page_Static_Controller

class Dummy_One_Page_Static_Plugin(InitPlugin):
    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        # reg it
        app_config.route_handlers.append(Dummy_One_Page_Static_Controller)
        return app_config
