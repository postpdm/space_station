from litestar.config.app import AppConfig

from .controller import XLS_Online_Controller
# take abstract
from app.plugins.abc_plugin import BasePlugin

class XLS_Online_Plugin(BasePlugin):
    # add routing
    controllers = [XLS_Online_Controller]

    fuser_title = 'Online xls-xlsx viewer-editor'
    fuser_description = 'Online xls-xlsx viewer-editor'