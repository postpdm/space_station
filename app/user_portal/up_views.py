from litestar import Controller, Request, get
from litestar.response import Template

USER_PORTAL_TEMPLATES_DIR = "user_portal/"

class User_Portal_Controller(Controller):
    path = "/"

    @get( )
    async def index_handler(self, request: Request) -> Template:
        cached_plugins = request.app.state.active_plugins

        return Template(
            template_name = USER_PORTAL_TEMPLATES_DIR + "index.html", 
            context={ 'cached_plugins' : cached_plugins }
        )

    @get( '/user_fav' )
    async def user_favs(self, request: Request) -> Template:
        #cached_plugins = request.app.state.active_plugins
        username = request.session.get("user_name")
 
        return Template(
            template_name = USER_PORTAL_TEMPLATES_DIR + "user_favs.html", 
            context={ 'username' : username }
        )
