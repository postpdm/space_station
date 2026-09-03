import importlib
import pkgutil
from pathlib import Path
import inspect

from litestar.plugins import InitPlugin

from space_station_stc.hull.plugin_abc.abc_plugin import BasePlugin

def discover_local_plugins( static_dir : str, plugin_packages : list ) -> list[InitPlugin]:
    """Find and load all local space station plugins from code base."""
    plugins: list[InitPlugin] = []

    def check_module( module_name : str ) -> None:
        # check module by name and if it's a correct plugin - load it
        try:
            module = importlib.import_module( module_name )
            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                if (
                    isinstance(attr, type)
                    and issubclass(attr, BasePlugin)  # Check for BasePlugin inheritance
                    and ( attr != BasePlugin ) # skip base
                    and not inspect.isabstract(attr)  # Skip abstract
                    and hasattr(attr, 'fplugin_id') # skip if plugin has no unique UUID
                ):
                    check_id = getattr(attr, 'fplugin_id')
                    for c in plugins:
                        c.fstatic_dir = static_dir
                        if c.fplugin_id == check_id:
                            raise Exception('Plugin ID is not unique, can not install')

                    # add to list
                    plugins.append(attr())

        except Exception as e:
            print(f"Error load plugin {module_name}: {e}")

    plugins_dir = Path(__file__).parent

    for _, module_name, is_pkg in pkgutil.iter_modules([str(plugins_dir)]):
        # Skip loader and abstract base
        if not is_pkg or module_name in ("loader", "abc_plugin"):
            continue

        check_module( f"app.plugins.{module_name}" )

    if plugin_packages:
        # load plugins from packages
        for pp in plugin_packages:
            spec = importlib.util.find_spec(pp)
            if spec is None:
                print(f"Error load plugin from package {pp}!")
            else:
                check_module( pp )

    return plugins
