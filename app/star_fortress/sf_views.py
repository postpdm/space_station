from litestar import Controller, Request, get
from litestar.response import Template

STAR_FORTRESS_TEMPLATES_DIR = "star_fortress/"

class Star_Fortress_Controller(Controller):
    path = "/star_fortress"

    @get('/')
    async def sf_index_handler(self, request: Request) -> Template:
        return Template(
            template_name = STAR_FORTRESS_TEMPLATES_DIR + "index.html",
            context={  }
        )

    @get('/gnn')
    async def sf_gnn(self, request: Request, ) -> Template:
        return Template(
            template_name = STAR_FORTRESS_TEMPLATES_DIR + "gnn.html",
            context={  }
        )
    
    @get('/crew')
    async def sf_crew(self, request: Request, ) -> Template:
        return Template(
            template_name = STAR_FORTRESS_TEMPLATES_DIR + "crew.html",
            context={  }
        )
    
    @get('/hull')
    async def sf_hull(self, request: Request, ) -> Template:
        # Access to app through request
        app_instance = request.app
        cached_plugins = request.app.state.active_plugins

        # Get all plugins
        plugin_names = [
            type(plugin).__name__ for plugin in app_instance.plugins.init
        ]

        return Template(
            template_name = STAR_FORTRESS_TEMPLATES_DIR + "hull.html",
            context={ 'installed_plugin_names' : plugin_names, 'cached_plugins' : cached_plugins }
        )
    
    @get('/wilderness_unvoid')
    async def sf_wilderness_unvoid(self, ) -> Template:
        return Template(
            template_name = STAR_FORTRESS_TEMPLATES_DIR + "wilderness_unvoid.html",
            context={ }
            )

    @get('/profile')
    async def sf_profile(self, request: Request, ) -> Template:

        user_login = request.session.get("user_login")
        user_name = request.session.get("user_name")
        user_id = request.session.get("user_id")


        return Template(
            template_name = STAR_FORTRESS_TEMPLATES_DIR + "profile.html",
            context={ 'user_id' : user_id, 'user_login' : user_login, 'user_name' : user_name }
            )


#