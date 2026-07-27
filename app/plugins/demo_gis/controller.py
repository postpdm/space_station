from litestar import Controller, get
from litestar.response import Template

DG_TEMPLATES_DIR = "demo_GIS/"

class Demo_GIS_Controller(Controller):
    path = "/demo_GIS"

    @get("/")
    async def user_homepahe(self) -> Template:
        return Template(
            template_name = DG_TEMPLATES_DIR + "demo_GIS.html", 
            context={  }
        )
    
    @get("/admin_panel")
    async def admin_panel(self) -> str:
        return "Hello dummy admin panel!"
