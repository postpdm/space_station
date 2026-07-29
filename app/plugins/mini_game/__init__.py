from litestar.config.app import AppConfig

from .controller import Mini_Game_Controller
# take abstract
from app.plugins.abc_plugin import BasePlugin

class Mini_Game_Plugin(BasePlugin):
    # add routing
    controllers = [Mini_Game_Controller]

    fuser_title = 'Tic-tak-toe'
    fuser_description = 'Tic-tak-toe min game'