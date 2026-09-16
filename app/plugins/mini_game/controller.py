from litestar import Controller, get
from litestar.response import Template

from space_station_stc.hull.plugin_abc.abc_controller import BasePluginController

DOPS_TEMPLATES_DIR = "mini_game/"


class Mini_Game_Controller(BasePluginController):
    path = "/tic_tac_toe"

    @get("/")
    async def user_homepage(self) -> Template:
        return Template(
            template_name = DOPS_TEMPLATES_DIR + "index.html",
            context={  }
        )

    @get("/admin_panel")
    async def admin_panel(self) -> str:
        return "Hello dummy admin panel!"

    async def plugin_health(self) -> bool:
        return True
