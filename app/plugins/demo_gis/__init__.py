from litestar.config.app import AppConfig

from .controller import Demo_GIS_Controller
# take abstract
from app.plugins.abc_plugin import BasePlugin

class Demo_GIS_Plugin(BasePlugin):
    # add routing
    controllers = [Demo_GIS_Controller]
    
    fuser_title = 'Demo GIS'
    fuser_description = 'Demo app with GIS functions'
#