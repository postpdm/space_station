from litestar import Controller, get
from litestar.response import Template

from app.plugins.abc_controller import BasePluginController

DG_TEMPLATES_DIR = "demo_GIS/"

class Demo_GIS_Controller(BasePluginController):
    path = "/demo_GIS"

    @get("/")
    async def user_homepage(self) -> Template:
        return Template(
            template_name = DG_TEMPLATES_DIR + "demo_GIS.html", 
            context={  }
        )
    
    @get("/admin_panel")
    async def admin_panel(self) -> str:
        return "Hello dummy admin panel!"
