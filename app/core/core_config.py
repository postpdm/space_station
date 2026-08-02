
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin

from advanced_alchemy.extensions.litestar import AsyncSessionConfig
from advanced_alchemy.extensions.litestar.session import SQLAlchemyAsyncSessionBackend

from litestar.middleware.session.server_side import ServerSideSessionConfig

from .core_models import WebSession

alchemy_config = SQLAlchemyAsyncConfig(
    connection_string="sqlite+aiosqlite:///space_station.sqlite",
    before_send_handler="autocommit",
    session_config=AsyncSessionConfig(expire_on_commit=False),
    create_all=True,
)

db_plugin = SQLAlchemyPlugin(config=alchemy_config )


# Session configuration
session_config_b = ServerSideSessionConfig(
    max_age=3600,  
)

# Session backend, store sessions in DB, session ID in cookies. Browser coockie know nothing about user
session_backend = SQLAlchemyAsyncSessionBackend(
    config=session_config_b,
    alchemy_config=alchemy_config,
    model=WebSession,
)


#