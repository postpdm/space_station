from litestar import Controller, get
from litestar.response import Template

DOPS_TEMPLATES_DIR = "dummy_one_page_static/"


class Dummy_One_Page_Static_Controller(Controller):
    path = "/dops"
    #tags = ["Authentication"]

    @get("/")
    async def user_homepahe(self) -> Template:
        return Template(
            template_name = DOPS_TEMPLATES_DIR + "calc.html", 
            context={  }
        )
    
    @get("/admin_panel")
    async def admin_panel(self) -> str:
        return "Hello dummy admin panel!"
