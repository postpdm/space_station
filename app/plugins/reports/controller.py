from uuid import UUID

from typing import Annotated, List

from litestar import Controller, get, post, Request, Response
from litestar.response import Template
from litestar.params import Dependency, PathParameter

from litestar.di import Provide, NamedDependency

from advanced_alchemy.extensions.litestar import (
    filters,
    providers,
    service,
)
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from sqlalchemy import text

from space_station_stc.hull.plugin_abc.abc_controller import BasePluginController

REPORTS_TEMPLATES_DIR = "reports/"

class Reports_Controller(BasePluginController):
    path = "/reports"

    @get("/report")
    async def get_report(
        self,        
        sql_report_database_session: NamedDependency[async_sessionmaker],
    ) -> dict:
        async with sql_report_database_session() as session:
            # get connection
            #async with await session.connection() as conn:                
                # create report table if not exists
            create_table_query = text("""
                    CREATE TABLE IF NOT EXISTS reports (
                        id SERIAL PRIMARY KEY,
                        product_name VARCHAR(255) NOT NULL,
                        quantity INT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # create table
            await session.execute(create_table_query)
                
                # commit
            await session.commit()            
            
            
            query = text("SELECT * FROM reports")
            result = await session.execute(query)
            data = result.scalars().all()
        return { "data" : data }


    @get("/")
    async def user_homepage(self) -> Template:
        return Template(
            template_name = REPORTS_TEMPLATES_DIR + "index.html",
            context={  }
        )

    @get("/admin_panel")
    async def admin_panel(self) -> str:
        return "Hello dummy admin panel!"

    async def plugin_health(self) -> bool:
        return True