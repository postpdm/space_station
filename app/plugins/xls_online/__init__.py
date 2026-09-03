from uuid import UUID

from litestar.config.app import AppConfig

from .controller import XLS_Online_Controller
# take abstract
from space_station_stc.hull.plugin_abc.abc_plugin import BasePlugin

class XLS_Online_Plugin(BasePlugin):
    # add routing
    controllers = [XLS_Online_Controller]

    fuser_title = 'Online xls-xlsx viewer-editor'
    fuser_description = 'Online xls-xlsx viewer-editor'
    
    fplugin_id = UUID( 'b29e71f4-3d8b-4b11-a083-725281729bfa' )
    
    fstatic_req = [ 'xls/xlsx.full.min.js' ]

#