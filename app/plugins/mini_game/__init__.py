from uuid import UUID

from litestar.config.app import AppConfig

from .controller import Mini_Game_Controller
# take abstract
from app.plugins.abc_plugin import BasePlugin

class Mini_Game_Plugin(BasePlugin):
    # add routing
    controllers = [Mini_Game_Controller]

    fuser_title = 'Tic-tac-toe'
    fuser_description = 'Tic-tac-toe mini game'
    fplugin_id = UUID( 'a52e8c19-7f34-4b12-9c88-54e1a0b3f892' )

#