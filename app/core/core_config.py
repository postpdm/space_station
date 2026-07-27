from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin

from advanced_alchemy.extensions.litestar import AsyncSessionConfig

alchemy_config = SQLAlchemyAsyncConfig(
    connection_string="sqlite+aiosqlite:///space_station.sqlite",
    before_send_handler="autocommit",
    session_config=AsyncSessionConfig(expire_on_commit=False),
    create_all=True,
)

db_plugin = SQLAlchemyPlugin(config=alchemy_config )