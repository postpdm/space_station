from litestar import Controller, get
from litestar.response import Template

from app.plugins.abc_controller import BasePluginController

CMS_TEMPLATES_DIR = "CMS/"


class CMS_Controller(BasePluginController):
    path = "/CMS"

    @get("/")
    async def user_homepage(self) -> Template:
        return Template(
            template_name = CMS_TEMPLATES_DIR + "index.html",
            context={  }
        )

    @get("/admin_panel")
    async def admin_panel(self) -> str:
        return "Hello dummy admin panel!"

    async def plugin_health(self) -> bool:
        return True
