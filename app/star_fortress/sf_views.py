from litestar import Controller, Request, get
from litestar.response import Template

STAR_FORTRESS_TEMPLATES_DIR = "star_fortress/"

class Star_Fortress_Controller(Controller):
    path = "/star_fortress"

    @get()
    async def index_handler(self, request: Request) -> Template:
        
        # Access to app through request
        app_instance = request.app
        cached_plugins = request.app.state.active_plugins

        # Get all plugins
        plugin_names = [
            type(plugin).__name__ for plugin in app_instance.plugins.init
        ]
        
        return Template(
            template_name = STAR_FORTRESS_TEMPLATES_DIR + "index.html", 
            context={ 'installed_plugin_names' : plugin_names, 'cached_plugins' : cached_plugins }
        )
