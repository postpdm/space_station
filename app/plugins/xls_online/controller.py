from litestar import Controller, get
from litestar.response import Template

from space_station_stc.hull.plugin_abc.abc_controller import BasePluginController

XLS_TEMPLATES_DIR = "xls_online/"

class XLS_Online_Controller(BasePluginController):
    path = "/xls_Online"

    @get("/")
    async def user_homepage(self) -> Template:
        return Template(
            template_name = XLS_TEMPLATES_DIR + "index.html",
            context={  }
        )

    @get("/admin_panel")
    async def admin_panel(self) -> str:
        return "Hello dummy admin panel!"

    async def plugin_health(self) -> bool:
        return True
