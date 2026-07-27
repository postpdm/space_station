from litestar.config.app import AppConfig

from .controller import Dummy_One_Page_Static_Controller
# take abstract
from app.plugins.abc_plugin import BasePlugin

class Dummy_One_Page_Static_Plugin(BasePlugin):
    # add routing
    controllers = [Dummy_One_Page_Static_Controller]

    fuser_title = 'Demo calculator'
    fuser_description = 'Demo app calculates mass accounting for temperature & pressure'