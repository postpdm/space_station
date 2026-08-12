from typing import Annotated
from pydantic import AfterValidator

from litestar import Controller, get
from litestar.response import Template

from litestar.exceptions import NotFoundException
  
from app.plugins.abc_controller import BasePluginController

DOPS_TEMPLATES_DIR = "dummy_one_page_static/"

def validate_latin(v: str) -> str:
    # isascii() only latin, isalpha() — only letters
    if not (v.isascii() and v.isalpha()):
        raise ValueError("Only latin letters allowed!")
    return v

# Validator
LatinStr = Annotated[str, AfterValidator(validate_latin)]

class Dummy_One_Page_Static_Controller(BasePluginController):
    path = "/dops"

    @get("/")
    async def user_homepage(self ) -> Template:
        return Template(
            template_name = DOPS_TEMPLATES_DIR + "index.html",
            context={  }
        )
        
    @get("/page/{page_template_name:str}")
    async def get_page(self, page_template_name : LatinStr ) -> Template:
        # check for Path Traversal attack
        verified_template_name = page_template_name
        if verified_template_name in [ 'mass_calc', 'pressure', 'mathlive' ]:
            return Template(
                template_name = DOPS_TEMPLATES_DIR + verified_template_name + ".html",
                context={  }
            )
        else:
            raise NotFoundException(detail="Page not found")

    @get("/admin_panel")
    async def admin_panel(self) -> str:
        return "Hello dummy admin panel!"

    async def plugin_health(self) -> bool:
        return True
