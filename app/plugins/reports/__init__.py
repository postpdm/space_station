from uuid import UUID

from litestar.config.app import AppConfig

from .controller import Reports_Controller
# take abstract
from space_station_stc.hull.plugin_abc.abc_plugin import BasePlugin

class Reports_Plugin(BasePlugin):
    # add routing
    controllers = [Reports_Controller]

    fuser_title = 'Reports demo'
    fuser_description = 'Reports demo'
    fplugin_id = UUID( 'a47ac10b-58cc-4372-b567-0e02b2c3d579' )

    # The plugin only declares the logical name.
    # Whether "report_database" is a Postgres or SQLite engine -
    # it's decided by build_sqlalchemy_fab in the core.
    fsql_connections = ["report_database"]

    fstatic_req = [ 'pico/2.1.1/pico.classless.min.css', 'pico/2.1.1/minimal-theme-switcher.js', 'pico/2.1.1/modals.js',
                    ### https://github.com/chartist-js/chartist
                    'charts/chartist/0.11.4/chartist.min.css',
                    'charts/chartist/0.11.4/chartist.min.js'
    ]
    
    def health(self) -> bool :
        return True

#
