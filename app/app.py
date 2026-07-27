from litestar import Litestar

from .config import template_config, static_config
from .user_portal.up_views import User_Portal_Controller
from .star_fortress.sf_views import Star_Fortress_Controller
from .core.core_config import db_plugin
from .core.core_view import NewsController

from .plugins import get_all_ss_plugins

plugins_list = get_all_ss_plugins()

app = Litestar( route_handlers=[User_Portal_Controller, Star_Fortress_Controller, NewsController],
                template_config=template_config,
                static_files_config=[static_config],
                plugins=[db_plugin] + plugins_list,
    )

app.state.active_plugins = plugins_list

#
