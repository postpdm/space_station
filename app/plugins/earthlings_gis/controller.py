from litestar import Controller, get
from litestar.response import Template

from space_station_stc.hull.plugin_abc.abc_controller import BasePluginController

from ...config import AppSettings

DG_TEMPLATES_DIR = "earthlings_gis/"

class Demo_GIS_Controller(BasePluginController):
    path = "/earthlings_gis"

    @get("/")
    async def user_homepage(self, app_settings: AppSettings) -> Template:
        if app_settings.GIS_USE_GEOSERVER:
            geoserver_cfg = {
              'projection'        : app_settings.PROJECTION,
              'tile_size'       : app_settings.TILE_SIZE,
              'wmts_attributions' : app_settings.WMTS_ATTRIBUTIONS,
              'wmts_url'          : app_settings.WMTS_URL,
              'wmts_layer'        : app_settings.WMTS_LAYER,
              'wms_url'           : app_settings.WMS_URL,
              'wms_layers'        : app_settings.WMS_LAYERS,
            }
        else:
            geoserver_cfg = {}

        return Template(
            template_name = DG_TEMPLATES_DIR + "earthlings_gis.html",
            context={ 'geoserver_cfg' : geoserver_cfg }
        )

    @get("/admin_panel")
    async def admin_panel(self) -> str:
        return "Hello dummy admin panel!"

    async def plugin_health(self) -> bool:
        return True
