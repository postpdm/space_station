import importlib
import pkgutil
from pathlib import Path
import inspect

from litestar.plugins import InitPlugin

from .abc_plugin import BasePlugin

def discover_local_plugins() -> list[InitPlugin]:
    """Find and load all local space station plugins from code base."""
    plugins: list[InitPlugin] = []
    plugins_dir = Path(__file__).parent
    
    for _, module_name, is_pkg in pkgutil.iter_modules([str(plugins_dir)]):
        # Skip loader and abstract base
        if not is_pkg or module_name in ("loader", "abc_plugin"):
            continue
            
        try:
            module = importlib.import_module(f"app.plugins.{module_name}")
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
                        if c.fplugin_id == check_id:
                            raise Exception('Plugin ID is not unique, can not install')
                            
                    # add to list
                    plugins.append(attr())
                    
        except Exception as e:
            print(f"Error load plugin {module_name}: {e}")
            
    return plugins
