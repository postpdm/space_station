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

    @get("/")
    async def user_homepage(
        self,
        sql_report_database_session: NamedDependency[async_sessionmaker],
    ) -> Template:
        async with sql_report_database_session() as session:
            # get connection
            #async with await session.connection() as conn:
                # create report table if not exists
            create_table_query = text("""
                    CREATE TABLE IF NOT EXISTS reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_name VARCHAR(255) NOT NULL,
                        quantity INT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # create table
            await session.execute(create_table_query)
            insert_query = text("""                    
                    INSERT INTO reports (product_name, quantity)
                    VALUES
                        ('Mouse', 10),
                        ('Mice', 25),
                        ('Dog', 40);
                """)
            await session.execute(insert_query)

                # commit
            await session.commit()

            query1 = text("SELECT * FROM reports")
            result1 = await session.execute(query1)
            data = result1.all()
            
            query2 = text("SELECT product_name, sum(quantity) as S FROM reports group by product_name")
            result2 = await session.execute(query2)
            data_graph = result2.all()

        return Template(
            template_name = REPORTS_TEMPLATES_DIR + "index.html",
            context={ "data" : data, "data_graph" : data_graph }
        )

    @get("/admin_panel")
    async def admin_panel(self) -> str:
        return "Hello dummy admin panel!"

    async def plugin_health(self) -> bool:
        return True