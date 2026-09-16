from pathlib import Path

from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin

from advanced_alchemy.extensions.litestar import AsyncSessionConfig
#from advanced_alchemy.extensions.litestar.session import SQLAlchemyAsyncSessionBackend

from litestar.middleware.session.server_side import ServerSideSessionConfig

from litestar.stores.file import FileStore

"""Core configuration: DB plugin, sessions, and SQL connection registry."""
from litestar.plugins.sqlalchemy import SQLAlchemyPlugin, SQLAlchemySyncConfig

from space_station_stc.hull.plugin_abc.sql_registry import SQLConnectionRegistry

#from .core_models import WebSession

# database
alchemy_config = SQLAlchemyAsyncConfig(
    connection_string="sqlite+aiosqlite:///space_station.sqlite",
    before_send_handler="autocommit",
    session_config=AsyncSessionConfig(expire_on_commit=False),
    create_all=True,
)

sql_registry = SQLConnectionRegistry()

def build_sqlalchemy_fab(
    *,
    report_database_url: str | None = None,
    audit_database_url: str | None = None,
    # ... whatever your real factory takes ...
) -> SQLConnectionRegistry:
    """
    Build SQLAlchemy engines/sessionmakers for the whole application and
    register them in the shared registry under logical names that plugins
    use in their `fsql_connections` declarations.
    """
    from sqlalchemy.ext.asyncio import create_async_engine

    report_database_url = "sqlite+aiosqlite:///rep.sqlite"

    # Register the report database, if configured.
    if report_database_url:
        report_engine = create_async_engine(report_database_url)
        sql_registry.register_engine("report_database", report_engine)

    # Register the audit database, if configured.
    if audit_database_url:
        audit_engine = create_async_engine(audit_database_url)
        sql_registry.register_engine("audit_db", audit_engine)

    # ... register any other named connections your factory knows about ...

    return sql_registry

db_plugin = SQLAlchemyPlugin(config=alchemy_config )

# session store

# Session configuration
session_config_b = ServerSideSessionConfig(
    max_age=60*60*24,  
)

session_store_config = { "sessions" : FileStore(path=Path("session_data"), create_directories=True ) }

#session_backend = session_config_b.middleware

# Session backend, store sessions in DB, session ID in cookies. Browser coockie know nothing about user
#session_backend = SQLAlchemyAsyncSessionBackend(
#    config=session_config_b,
    #alchemy_config=alchemy_config,
    #model=WebSession,
#)


#