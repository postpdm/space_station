from uuid import UUID

from typing import Annotated

from litestar import Controller, get, post, Request
from litestar.response import Template
from litestar.params import Dependency, PathParameter

from litestar.di import Provide

from advanced_alchemy.extensions.litestar import (
    filters,
    providers,
    service,
)

from app.plugins.abc_controller import BasePluginController

CMS_TEMPLATES_DIR = "cms/"

from .service import CMSService, CMS_Section_Service
from .schema import Page_pdnt, PageCreate_pdnt, Page_with_sections_pdnt, Page_Section_pdnt, Page_Section_Create_pdnt

from .parsers import CONST_PLAIN_MARKDOWN

from .service_special import provide_file_service, TextFileService

SPECIAL_HELP_PAGE = 'help'

class CMS_Controller(BasePluginController):
    path = "/cms"

    # this mega structure just import 2 dependencies
    dependencies = {
        **providers.create_service_dependencies(
            CMSService,
            "CMS_service",
            filters={"pagination_type": "limit_offset", "id_filter": UUID, "search": "title", "search_ignore_case": True},
        ),

        **providers.create_service_dependencies(
            CMS_Section_Service,
            "CMS_Section_Service",
        ),

        "file_service": Provide(provide_file_service),
    }

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
            context={ 'special_page' : False,
                      'page_id' : page_id,
                      'Enable_edit_flag' : True }
        )

    @get("/special/help")
    async def view_page_spetial_help(self) -> Template:
        return Template(
            template_name = CMS_TEMPLATES_DIR + "view_page.html",
            context={ 'special_page' : True,
                      'page_id' : SPECIAL_HELP_PAGE,
                      'Enable_edit_flag' : False }
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

    @get("/get_page_api/{page_id:uuid}")
    async def get_page_api(self, CMS_service: CMSService, page_id:UUID) -> Page_with_sections_pdnt:
        obj = await CMS_service.get_one_or_none( id = page_id )
        return CMS_service.to_schema( obj, schema_type=Page_with_sections_pdnt)

    @get("/get_special_page_api/{page_id:str}")
    async def get_special_page_api(self, file_service: TextFileService, page_id:str) -> Page_with_sections_pdnt:
        p = "docs/cms/help.md"
        obj = await file_service.get_data( p )
        return obj

    @post(path="/new_page_api")
    async def create_new_page_api(self, request : Request, CMS_service: CMSService, data: PageCreate_pdnt) -> Page_pdnt:
        """Create a new page."""
        obj = await CMS_service.create( data )
        return CMS_service.to_schema(obj, schema_type=Page_pdnt)

    @post(path="/new_page_section_api/{page_id:uuid}")
    async def create_new_page_section_api(self, request : Request, CMS_Section_Service: CMS_Section_Service, page_id : UUID, data: Page_Section_Create_pdnt) -> Page_Section_pdnt:
        """Create a new page section."""

        section_data_dict = data.model_dump()
        section_data_dict[ "page_id" ] = page_id
        section_data_dict[ "content_type" ] = CONST_PLAIN_MARKDOWN

        obj = await CMS_Section_Service.create( section_data_dict )
        return CMS_Section_Service.to_schema(obj, schema_type=Page_Section_pdnt)
#