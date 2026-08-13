from uuid import UUID

from litestar.config.app import AppConfig

from .controller import CMS_Controller
# take abstract
from app.plugins.abc_plugin import BasePlugin

class CMS_Plugin(BasePlugin):
    # add routing
    controllers = [CMS_Controller]

    fuser_title = 'CMS'
    fuser_description = 'Content management'
    fplugin_id = UUID( '6def0698-aa92-45f7-b0b7-946b59845dce' )

#