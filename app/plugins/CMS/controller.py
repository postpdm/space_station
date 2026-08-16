from uuid import UUID

from typing import Annotated

from litestar import Controller, get
from litestar.response import Template
from litestar.params import Dependency, PathParameter

from advanced_alchemy.extensions.litestar import (
    filters,
    providers,
    service,
)

from app.plugins.abc_controller import BasePluginController

CMS_TEMPLATES_DIR = "CMS/"

from .service import CMSService
from .schema import Page_pdnt

class CMS_Controller(BasePluginController):
    path = "/CMS"

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

    @get("/admin_panel")
    async def admin_panel(self) -> str:
        return "Hello dummy admin panel!"

    async def plugin_health(self) -> bool:
        return True

    @get(path="/get_pages")
    async def list_pages(
        self,
        CMS_service: CMSService,
        filters: Annotated[list[filters.FilterTypes], Dependency(skip_validation=True)],
    ) -> service.OffsetPagination[Page_pdnt]:
        """List pages."""
        results, total = await CMS_service.get_many_and_count(*filters)
        return CMS_service.to_schema(results, total, filters=filters, schema_type=Page_pdnt)

#