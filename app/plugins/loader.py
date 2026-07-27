import importlib
import pkgutil
from pathlib import Path
from litestar.plugins import InitPlugin

def discover_local_plugins() -> list[InitPlugin]:
    """Find and load all local space station plugins from code base."""
    plugins: list[InitPlugin] = []
    
    # get plugin dir
    plugins_dir = Path(__file__).parent
    
    # Scan for plugins
    for _, module_name, is_pkg in pkgutil.iter_modules([str(plugins_dir)]):
        if not is_pkg or module_name == "loader":
            continue
            
        try:
            # Import
            module = importlib.import_module(f"app.plugins.{module_name}")
            
            # Find InitPlugin
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                if (
                    isinstance(attr, type) 
                    and issubclass(attr, InitPlugin) 
                    and attr is not InitPlugin
                ):
                    # Init and add to list
                    plugins.append(attr())
                    
        except Exception as e:
            # Error
            print(f"Error load plugin {module_name}: {e}")
            
    return plugins
