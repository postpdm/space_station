
from litestar import Litestar
#from litestar.config.allowed_hosts import AllowedHostsConfig
from litestar.di import Provide
#from litestar.middleware.session import SessionMiddleware
from litestar.exceptions.http_exceptions import NotAuthorizedException

from functools import partial

from .config import template_config, static_config, get_settings
from .user_portal.up_views import User_Portal_Controller
from .star_fortress.sf_views import Star_Fortress_Controller
from .core.core_config import db_plugin, session_config_b, session_store_config, sql_registry, build_sqlalchemy_fab # session_backend
from .core.core_view import NewsController, UserController, UserFavController
from .core.core_auth import auth_mw, auth_exception_handler

from .core.cage.cage_view import  CageController

from .plugins import get_all_ss_plugins
from .plugins.loader import build_global_sql_dependencies, validate_plugin_connections

from .views import favicon

from .star_fortress.inner_circle.context import db_encryption_key

settings = get_settings()

if settings.inner_circle_key:
    db_encryption_key.set( settings.inner_circle_key )
else:
    print("Secrets settings not found!")
    raise SystemExit(1)

# Security: Limit domains to prevent HTTP Host Header attacks
# host_config = AllowedHostsConfig(
#    allowed_hosts=settings.allowed_hosts,
#    exclude=["/health"] # Allow load balancer checks
#)

# Discover plugins. The registry is intentionally empty here:
#    plugin bundles will be resolved in on_startup, after reading
#    the primary database.
plugins_list = get_all_ss_plugins( settings, None )

# Build lazy SQL DI providers from fsql_connections (names only).
# Safe to call before the registry is populated.
plugin_sql_deps = build_global_sql_dependencies(plugins_list)


# on_startup: read external_db, build lazy engines, hand bundles out.
# No external DB is contacted here.
async def init_plugin_sql_connections() -> None:
    await build_sqlalchemy_fab(registry=sql_registry, fail_fast=True)

    for plugin in plugins_list:
        if hasattr(plugin, "fsql_connections"):
            plugin.fsql_provided = sql_registry.resolve(
                list(plugin.fsql_connections)
            )

    validate_plugin_connections(plugins_list, sql_registry)


#print("Registered SQL names:", sql_registry.all_names())


app = Litestar( debug=settings.litestar_debug, # Hard disable debug mode in prod!
                # allowed_hosts=host_config,

                # Inject settings globally via dependency injection
                dependencies={ "app_settings": Provide(get_settings, use_cache=True, sync_to_thread=False ),
                               # Plugin SQL providers: sql_<name>_engine / sql_<name>_session.
                               **plugin_sql_deps
                },
                #middleware=[partial(SessionMiddleware, backend=session_backend), auth_mw],
                middleware=[session_config_b.middleware, auth_mw],
                stores=session_store_config,
                exception_handlers={NotAuthorizedException: auth_exception_handler},

                route_handlers=[ favicon,
                                 UserController, UserFavController, User_Portal_Controller, Star_Fortress_Controller, NewsController, CageController],
                template_config=template_config,
                static_files_config=[static_config],
                plugins=[db_plugin] + plugins_list,
                on_startup=[init_plugin_sql_connections],
                on_shutdown=[sql_registry.dispose_all],
    )

app.state.active_plugins = plugins_list
app.state.sql_registry = sql_registry   # useful for admin / diagnostics

#
