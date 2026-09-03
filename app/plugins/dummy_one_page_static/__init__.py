from uuid import UUID

from litestar.config.app import AppConfig

from .controller import Dummy_One_Page_Static_Controller
# take abstract
from space_station_stc.hull.plugin_abc.abc_plugin import BasePlugin

class Dummy_One_Page_Static_Plugin(BasePlugin):
    # add routing
    controllers = [Dummy_One_Page_Static_Controller]

    fuser_title = 'Demo calculator'
    fuser_description = 'Demo app calculates mass accounting for temperature & pressure'
    fplugin_id = UUID( '123e4567-e89b-12d3-a456-426614174000' )

    fstatic_req = [ 'cosmos/cosmic_racoon_slide_rule.jpeg', 'math/mathlive/0.110.0/mathlive.js', 'math/mathlive/0.110.0/esm.js' ]

#