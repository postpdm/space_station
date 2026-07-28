from litestar import Litestar
#from litestar.config.allowed_hosts import AllowedHostsConfig
from litestar.di import Provide

from .config import template_config, static_config, get_settings
from .user_portal.up_views import User_Portal_Controller
from .star_fortress.sf_views import Star_Fortress_Controller
from .core.core_config import db_plugin
from .core.core_view import NewsController

from .plugins import get_all_ss_plugins

settings = get_settings()

# Security: Limit domains to prevent HTTP Host Header attacks
# host_config = AllowedHostsConfig(
#    allowed_hosts=settings.allowed_hosts,
#    exclude=["/health"] # Allow load balancer checks
#)

plugins_list = get_all_ss_plugins()

app = Litestar( debug=settings.litestar_debug, # Hard disable debug mode in prod!
                # allowed_hosts=host_config,
                
                # Inject settings globally via dependency injection
                dependencies={"app_settings": Provide(get_settings, use_cache=True, sync_to_thread=False )},
                
                route_handlers=[User_Portal_Controller, Star_Fortress_Controller, NewsController],
                template_config=template_config,
                static_files_config=[static_config],
                plugins=[db_plugin] + plugins_list,
    )

app.state.active_plugins = plugins_list

#
