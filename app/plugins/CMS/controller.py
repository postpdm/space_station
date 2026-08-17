from uuid import UUID

from typing import Annotated

from litestar import Controller, get, post, Request
from litestar.response import Template
from litestar.params import Dependency, PathParameter

from advanced_alchemy.extensions.litestar import (
    filters,
    providers,
    service,
)

from app.plugins.abc_controller import BasePluginController

CMS_TEMPLATES_DIR = "cms/"

from .service import CMSService
from .schema import Page_pdnt, NewPageCreate_pdnt

class CMS_Controller(BasePluginController):
    path = "/cms"

    dependencies = providers.create_service_dependencies(
        CMSService,
        "CMS_service",
        #load=[GNN_Article_Model.sections],
        filters={"pagination_type": "limit_offset", "id_filter": UUID, "search": "title", "search_ignore_case": True},
    )


    @get("/")
    async def user_homepage(self) -> Template:
        return Template(
            template_name = CMS_TEMPLATES_DIR + "index.html",
            context={  }
        )

    @get("/page/{page_id:uuid}")
    async def view_page(self, page_id:UUID) -> Template:
        return Template(
            template_name = CMS_TEMPLATES_DIR + "view_page.html",
            context={ 'page_id' : page_id }
        )

    @get("/admin_panel")
    async def admin_panel(self) -> str:
        return "Hello dummy admin panel!"

    async def plugin_health(self) -> bool:
        return True

    @get(path="/get_pages_api")
    async def get_pages_api(
        self,
        CMS_service: CMSService,
        filters: Annotated[list[filters.FilterTypes], Dependency(skip_validation=True)],
    ) -> service.OffsetPagination[Page_pdnt]:
        """List pages."""
        results, total = await CMS_service.get_many_and_count(*filters)
        return CMS_service.to_schema(results, total, filters=filters, schema_type=Page_pdnt)

    @get("/new_page")
    async def new_page(self) -> Template:
        return Template(
            template_name = CMS_TEMPLATES_DIR + "new_page.html",
            context={  }
        )
        
    @post(path="/new_page_api")
    async def create_new_page_api(self, request : Request, CMS_service: CMSService, data: NewPageCreate_pdnt) -> Page_pdnt:
        """Create a new page."""
        user_id = request.session.get("user_id")
        new_page_dict = data.model_dump()
        new_page_dict[ "created_user_id" ] = UUID( user_id )

        obj = await CMS_service.create( new_page_dict )
        return CMS_service.to_schema(obj, schema_type=Page_pdnt)

#