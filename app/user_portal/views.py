from litestar import Controller, get
from litestar.response import Template

USER_PORTAL_TEMPLATES_DIR = "user_portal/"

class User_Portal_Controller(Controller):
    path = "/"

    @get()
    async def index_handler(self) -> Template:
        return Template(
            template_name = USER_PORTAL_TEMPLATES_DIR + "index.html", 
            context={  }
        )
