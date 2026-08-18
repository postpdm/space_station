from litestar import Controller, get
from litestar.response import Template

from app.plugins.abc_controller import BasePluginController

DG_TEMPLATES_DIR = "demo_gis/"

class Demo_GIS_Controller(BasePluginController):
    path = "/demo_gis"

    @get("/")
    async def user_homepage(self) -> Template:
        geoserver_cfg = { 'proj' : 'EPSG:3857',
                          'size' : 256,


                           };

        return Template(
            template_name = DG_TEMPLATES_DIR + "demo_gis.html",
            context={ 'geoserver_cfg' :geoserver_cfg }
        )

    @get("/admin_panel")
    async def admin_panel(self) -> str:
        return "Hello dummy admin panel!"

    async def plugin_health(self) -> bool:
        return True
