# https://docs.litestar.dev/2/usage/plugins/index.html

from litestar.plugins import InitPlugin

from .loader import discover_local_plugins

from ..config import STATIC_DIR, AppSettings

def get_all_ss_plugins( app_settings: AppSettings ) -> list[InitPlugin]:
    """Collect all local space_station plugins."""

    local_plugins = discover_local_plugins( STATIC_DIR, app_settings.plugin_packages )

    return local_plugins
