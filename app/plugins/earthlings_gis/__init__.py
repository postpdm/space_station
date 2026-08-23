from uuid import UUID

from litestar.config.app import AppConfig

from .controller import Demo_GIS_Controller
# take abstract
from app.plugins.abc_plugin import BasePlugin

class Demo_GIS_Plugin(BasePlugin):
    # add routing
    controllers = [Demo_GIS_Controller]
    
    fuser_title = 'Demo GIS'
    fuser_description = 'Demo app with GIS functions'
    
    fplugin_id = UUID( '7c1b3f54-2e91-4a43-8f5b-12d8a9f03cde' )

    fstatic_req = [ 'ol/ol.css', 'ol/ol.js' ]
#
