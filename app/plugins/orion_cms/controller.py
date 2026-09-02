from uuid import UUID

from typing import Annotated, List

from litestar import Controller, get, post, Request, Response
from litestar.response import Template
from litestar.params import Dependency, PathParameter

from litestar.di import Provide

from advanced_alchemy.extensions.litestar import (
    filters,
    providers,
    service,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.plugins.abc_controller import BasePluginController

CMS_TEMPLATES_DIR = "orion_cms/"

from .service import CMSTreeService, CMSService, CMS_Section_Service, CMS_ReportService, provide_cms_report_service
from .schema import Page_Tree_Node_pdnt, Page_pdnt, Tree_Node_Create_pdnt, Tree_Node_Update_pdnt, PageCreate_pdnt, PageUpdate_pdnt, Page_with_sections_pdnt, Page_Section_pdnt, Page_Section_Create_pdnt,Page_Section_Update_pdnt, Orion_Pages_Stat_Count_pdnt, Orion_Pages_Stat_By_Day_pdnt, Orion_Manuscript_CodeRequest_pdnt

from .parsers import CONST_PLAIN_MARKDOWN, execute_orion_manusctript

from .service_special import provide_file_service, TextFileService

SPECIAL_HELP_PAGE = 'help'

class CMS_Controller(BasePluginController):
    path = "/cms"

    # this mega structure just import 2 dependencies
    dependencies = {
        **providers.create_service_dependencies(
            CMSTreeService,
            "cms_tree_service",
            filters={"pagination_type": "limit_offset", "id_filter": UUID, "search": "title", "search_ignore_case": True},
        ),
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
        "cms_report_service": Provide(provide_cms_report_service)
    }

    @get("/")
    async def user_homepage(self) -> Template:
        return Template(
            template_name = CMS_TEMPLATES_DIR + "index.html",
            context={  }
        )

    @get("/tree_node_page/{tree_node_id:uuid}")
    async def view_tree_node_page(self, tree_node_id:UUID) -> Template:
        return Template(
            template_name = CMS_TEMPLATES_DIR + "view_tree_node.html",
            context={ 'special_page' : False,
                      'tree_node_id' : tree_node_id,
                      'Enable_edit_flag' : True }
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
    async def view_page_special_help(self) -> Template:
        return Template(
            template_name = CMS_TEMPLATES_DIR + "view_page.html",
            context={ 'special_page' : True,
                      'page_id' : SPECIAL_HELP_PAGE,
                      'Enable_edit_flag' : False }
        )

    @get("/special/stat")
    async def view_page_special_stat(self) -> Template:
        return Template(
            template_name = CMS_TEMPLATES_DIR + "stat_page.html",
            context={ }
        )

    @get("/admin_panel")
    async def admin_panel(self) -> str:
        return "Hello dummy admin panel!"

    async def plugin_health(self) -> bool:
        return True

    @get(path="/get_page_tree_api")
    async def get_page_tree_api(
        self,
        cms_tree_service: CMSTreeService,
        filters: Annotated[list[filters.FilterTypes], Dependency(skip_validation=True)],
    ) -> service.OffsetPagination[Page_Tree_Node_pdnt]:
        """Tree."""
        results, total = await cms_tree_service.get_many_and_count(*filters)
        return cms_tree_service.to_schema(results, total, filters=filters, schema_type=Page_Tree_Node_pdnt)

    @get(path="/get_all_pages_api")
    async def get_all_pages_api(
        self,
        CMS_service: CMSService,
        filters: Annotated[list[filters.FilterTypes], Dependency(skip_validation=True)],
    ) -> service.OffsetPagination[Page_pdnt]:
        """List all pages."""
        results, total = await CMS_service.get_many_and_count(*filters)
        return CMS_service.to_schema(results, total, filters=filters, schema_type=Page_pdnt)


    @get(path="/get_one_node_pages_api/{node_id:uuid}")
    async def get_one_node_pages_api(
        self,
        node_id:UUID,
        CMS_service: CMSService,
        filters: Annotated[list[filters.FilterTypes], Dependency(skip_validation=True)],
    ) -> service.OffsetPagination[Page_pdnt]:
        """List pages in current tree node."""

        results, total = await CMS_service.get_many_and_count(*filters, tree_id=node_id)
        return CMS_service.to_schema(results, total, filters=filters, schema_type=Page_pdnt)

    @get("/new_tree_node")
    async def new_tree_node(self) -> Template:
        return Template(
            template_name = CMS_TEMPLATES_DIR + "new_tree_node.html",
            context={ 'create_mode' : True, }
        )
    @get("/edit_tree_node/{node_id:uuid}")
    async def edit_tree_node(self, cms_tree_service: CMSTreeService, node_id:UUID) -> Template:
        node = await cms_tree_service.get_one_or_none( id = node_id )
        return Template(
            template_name = CMS_TEMPLATES_DIR + "new_tree_node.html",
            context={ 'create_mode' : False, 'node_id' : node_id, 'node' : node }
        )


    @get("/new_page/{tree_node_id:uuid}")
    async def new_page(self, tree_node_id: UUID ) -> Template:
        return Template(
            template_name = CMS_TEMPLATES_DIR + "new_page.html",
            context={ 'create_mode' : True, 'tree_node_id' : tree_node_id }
        )

    @get("/edit_page/{page_id:uuid}")
    async def edit_page(self, CMS_service: CMSService, page_id:UUID) -> Template:
        page = await CMS_service.get_one_or_none( id = page_id )
        return Template(
            template_name = CMS_TEMPLATES_DIR + "new_page.html",
            context={ 'create_mode' : False, 'page_id' : page_id, 'page' : page }
        )

    @get("/get_page_api/{page_id:uuid}")
    async def get_page_api(self, CMS_service: CMSService, page_id:UUID) -> Page_with_sections_pdnt:
        obj = await CMS_service.get_one_or_none( id = page_id )
        return CMS_service.to_schema( obj, schema_type=Page_with_sections_pdnt)

    @get("/get_special_page_api/{page_id:str}")
    async def get_special_page_api(self, file_service: TextFileService, page_id:str) -> Page_with_sections_pdnt:
        p = "docs/orion_cms/help.md"
        obj = await file_service.get_data( p )
        return obj

    @post(path="/new_tree_node_api")
    async def create_new_tree_node_api(self, request : Request, cms_tree_service: CMSTreeService, data: Tree_Node_Create_pdnt) -> Page_Tree_Node_pdnt:
        """Create a new tree node."""
        obj = await cms_tree_service.create( data )
        return cms_tree_service.to_schema(obj, schema_type=Page_Tree_Node_pdnt)

    @post(path="/update_tree_node_api/{node_id:uuid}")
    async def update_tree_node_api(self, node_id:UUID, request : Request, cms_tree_service: CMSTreeService, data: Tree_Node_Update_pdnt) -> Page_Tree_Node_pdnt:
        """Updtate tree node."""
        obj = await cms_tree_service.update(data, item_id=node_id, auto_commit=True)
        return cms_tree_service.to_schema(obj, schema_type=Page_Tree_Node_pdnt)

    @post(path="/new_page_api/{node_id:uuid}")
    async def create_new_page_api(self, node_id:UUID, request : Request, CMS_service: CMSService, data: PageCreate_pdnt) -> Page_pdnt:
        """Create a new page."""
        data_dict = data.model_dump()
        data_dict[ "tree_id" ] = node_id
        obj = await CMS_service.create( data_dict )
        return CMS_service.to_schema(obj, schema_type=Page_pdnt)

    @post(path="/update_page_api/{page_id:uuid}")
    async def update_page_api(self, page_id:UUID, request : Request, CMS_service: CMSService, data: PageUpdate_pdnt) -> Page_pdnt:
        """Updtate page."""
        obj = await CMS_service.update(data, item_id=page_id, auto_commit=True)
        return CMS_service.to_schema(obj, schema_type=Page_pdnt)

    @post(path="/new_page_section_api/{page_id:uuid}")
    async def create_new_page_section_api(self, request : Request, CMS_Section_Service: CMS_Section_Service, page_id : UUID, data: Page_Section_Create_pdnt) -> Page_Section_pdnt:
        """Create a new page section."""

        section_data_dict = data.model_dump()
        section_data_dict[ "page_id" ] = page_id
        section_data_dict[ "content_type" ] = CONST_PLAIN_MARKDOWN

        obj = await CMS_Section_Service.create( section_data_dict )
        return CMS_Section_Service.to_schema(obj, schema_type=Page_Section_pdnt)
        
    @post(path="/update_page_section_api/{section_id:uuid}")
    async def update_page_section_eapi(self, section_id:UUID, request : Request, CMS_Section_Service: CMS_Section_Service, data: Page_Section_Update_pdnt) -> Page_Section_pdnt:
        """Updtate page."""
        obj = await CMS_Section_Service.update(data, item_id=section_id, auto_commit=True)
        return CMS_Section_Service.to_schema(obj, schema_type=Page_Section_pdnt)


    @get("/get_statistics_api_page_count")
    async def get_statistics_api_page_count(self, cms_report_service: CMS_ReportService ) -> Orion_Pages_Stat_Count_pdnt:
        return cms_report_service.get_page_count()

    @get("/get_statistics_api_page_created_by_day")
    async def get_statistics_api_page_created_by_day(self, cms_report_service: CMS_ReportService ) -> List[Orion_Pages_Stat_By_Day_pdnt]:
        return cms_report_service.get_page_by_day_count()

    @post("/build_component")
    async def build_component(self, data : Orion_Manuscript_CodeRequest_pdnt, db_session: AsyncSession ) -> Response:
        try:
            code = data.code
            component_hmtl_str = await execute_orion_manusctript( code, db_session )
            return Response( content = component_hmtl_str, media_type = "text/html", status_code = 200 )
        except Exception as e:
            return Response( content = 'Error building component', media_type = "text/html", status_code = 500 )

#