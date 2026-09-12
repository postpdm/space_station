from uuid import UUID

from litestar import Controller, Request, get, post
from litestar.response import Template

from advanced_alchemy.extensions.litestar import (
    filters,
    providers,
    service,
)

from .inner_circle import models
from .inner_circle.schema import ExternalDB_pdnt
from .inner_circle.service import ExternalDBService

STAR_FORTRESS_TEMPLATES_DIR = "star_fortress/"

class Star_Fortress_Controller(Controller):
    path = "/star_fortress"

    # this mega structure just import dependencies
    dependencies = {
        **providers.create_service_dependencies(
            ExternalDBService,
            "externaldbservice",
            filters={"pagination_type": "limit_offset", "id_filter": UUID, "search": "title", "search_ignore_case": True},
        ),
    }

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
    async def sf_wilderness_unvoid(self, externaldbservice : ExternalDBService ) -> Template:
        external_db = await externaldbservice.list()
        return Template(
            template_name = STAR_FORTRESS_TEMPLATES_DIR + "wilderness_unvoid.html",
            context={ 'external_db' : external_db }
            )

    @get('/wilderness_unvoid/add_new_external_db')
    async def sf_wilderness_unvoid_add_new_external_db(self ) -> Template:
        return Template(
            template_name = STAR_FORTRESS_TEMPLATES_DIR + "wilderness_unvoid_add_new_external_db.html",
            context={ }
            )

    @get('/wilderness_unvoid/edit_external_db/{external_db_id:uuid}')
    async def sf_wilderness_unvoid_edit_external_db(self, external_db_id : UUID, externaldbservice : ExternalDBService ) -> Template:
        external_db = await externaldbservice.get( external_db_id )
        return Template(
            template_name = STAR_FORTRESS_TEMPLATES_DIR + "wilderness_unvoid_add_new_external_db.html",
            context={ "external_db" : external_db }
            )

    @get('/wilderness_unvoid/view_external_db/{external_db_id:uuid}')
    async def sf_wilderness_unvoid_view_external_db(self, external_db_id : UUID, externaldbservice : ExternalDBService ) -> Template:
        external_db = await externaldbservice.get( external_db_id )
        return Template(
            template_name = STAR_FORTRESS_TEMPLATES_DIR + "wilderness_unvoid_view_external_db.html",
            context={ "external_db" : external_db }
            )

    @post(path="/wilderness_unvoid/inner_circle/reg_new_external_db")
    async def reg_new_external_db(self, request : Request, externaldbservice : ExternalDBService, data: ExternalDB_pdnt) -> ExternalDB_pdnt:
        """Reg a new external db."""
        obj = await externaldbservice.create( data )
        return externaldbservice.to_schema(obj, schema_type=ExternalDB_pdnt)

    @post('/wilderness_unvoid/inner_circle/update_external_db/{external_db_id:uuid}')
    async def update_external_db(
        self,
        external_db_id:UUID,
        externaldbservice : ExternalDBService,
        data: ExternalDB_pdnt,
    ) -> ExternalDB_pdnt:
        """Update external db."""
        obj = await externaldbservice.update(data, item_id=external_db_id, auto_commit=True)
        return externaldbservice.to_schema(obj, schema_type=ExternalDB_pdnt)

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