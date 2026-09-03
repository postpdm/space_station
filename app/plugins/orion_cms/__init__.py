from uuid import UUID

from litestar.config.app import AppConfig

from .controller import CMS_Controller
# take abstract
from space_station_stc.hull.plugin_abc.abc_plugin import BasePlugin

class CMS_Plugin(BasePlugin):
    # add routing
    controllers = [CMS_Controller]

    fuser_title = 'Orion CMS'
    fuser_description = 'Orion - Content Management System'
    fplugin_id = UUID( '6def0698-aa92-45f7-b0b7-946b59845dce' )

    fstatic_req = [ 'pico/2.1.1/pico.classless.min.css', 'pico/2.1.1/minimal-theme-switcher.js', 'pico/2.1.1/modals.js',
                    'markdown/marked/18.0.9/marked.umd.js', 
                    'markdown/mermaid/11.17.0/mermaid.min.js',
                    ### https://github.com/chartist-js/chartist
                    'charts/chartist/0.11.4/chartist.min.css',
                    'charts/chartist/0.11.4/chartist.min.js'
    ]

#
