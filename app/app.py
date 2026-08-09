
from litestar import Litestar
#from litestar.config.allowed_hosts import AllowedHostsConfig
from litestar.di import Provide
#from litestar.middleware.session import SessionMiddleware
from litestar.exceptions.http_exceptions import NotAuthorizedException

from functools import partial


from .config import template_config, static_config, get_settings
from .user_portal.up_views import User_Portal_Controller
from .star_fortress.sf_views import Star_Fortress_Controller
from .core.core_config import db_plugin, session_config_b, session_store_config # session_backend 
from .core.core_view import NewsController, UserController, UserFavController
from .core.core_auth import auth_mw, auth_exception_handler

from .plugins import get_all_ss_plugins

from .views import favicon

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
                #middleware=[partial(SessionMiddleware, backend=session_backend), auth_mw],
                middleware=[session_config_b.middleware, auth_mw],
                stores=session_store_config,
                exception_handlers={NotAuthorizedException: auth_exception_handler},

                route_handlers=[ favicon,
                                 UserController, UserFavController, User_Portal_Controller, Star_Fortress_Controller, NewsController],
                template_config=template_config,
                static_files_config=[static_config],
                plugins=[db_plugin] + plugins_list,
    )

app.state.active_plugins = plugins_list

#
