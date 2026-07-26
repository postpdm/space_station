from litestar import Controller, get
from litestar.response import Template

STAR_FORTRESS_TEMPLATES_DIR = "star_fortress/"

class Star_Fortress_Controller(Controller):
    path = "/star_fortress"

    @get()
    async def index_handler(self) -> Template:
        return Template(
            template_name = STAR_FORTRESS_TEMPLATES_DIR + "index.html", 
            context={  }
        )
