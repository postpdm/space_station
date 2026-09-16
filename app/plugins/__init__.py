# https://docs.litestar.dev/2/usage/plugins/index.html

from litestar.plugins import InitPlugin

from .loader import discover_local_plugins

from ..config import STATIC_DIR, AppSettings
from space_station_stc.hull.plugin_abc.sql_registry import SQLConnectionRegistry


def get_all_ss_plugins(
    app_settings: AppSettings,
    sql_registry: SQLConnectionRegistry,
) -> list[InitPlugin]:
    """Collect all space_station plugins, injecting SQL connections."""

    local_plugins = discover_local_plugins(
        STATIC_DIR,
        app_settings.plugin_packages,
        sql_registry=sql_registry,
    )

    return local_plugins
    