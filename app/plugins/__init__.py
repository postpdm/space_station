# https://docs.litestar.dev/2/usage/plugins/index.html

from litestar.plugins import InitPlugin

from .loader import discover_local_plugins

def get_all_ss_plugins() -> list[InitPlugin]:
    """Collect all local space_station plugins."""
    
    local_plugins = discover_local_plugins()
    
    return local_plugins
