from pathlib import Path

from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin

from advanced_alchemy.extensions.litestar import AsyncSessionConfig
#from advanced_alchemy.extensions.litestar.session import SQLAlchemyAsyncSessionBackend
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select

from litestar.middleware.session.server_side import ServerSideSessionConfig

from litestar.stores.file import FileStore

"""Core configuration: DB plugin, sessions, and SQL connection registry."""
from litestar.plugins.sqlalchemy import SQLAlchemyPlugin, SQLAlchemySyncConfig

from space_station_stc.hull.plugin_abc.sql_registry import SQLConnectionRegistry
from app.star_fortress.inner_circle.models import ExternalDB   # external databases list

#from .core_models import WebSession

# Primary application DB config
alchemy_config = SQLAlchemyAsyncConfig(
    connection_string="sqlite+aiosqlite:///space_station.sqlite",
    before_send_handler="autocommit",
    session_config=AsyncSessionConfig(expire_on_commit=False),
    create_all=True,
)

db_plugin = SQLAlchemyPlugin(config=alchemy_config )

# Session configuration
session_config_b = ServerSideSessionConfig(
    max_age=60*60*24,  
)

# The one shared registry used by plugins.
sql_registry = SQLConnectionRegistry()

async def build_sqlalchemy_fab(
    *,
    registry: SQLConnectionRegistry | None = None,
    fail_fast: bool = True,
) -> SQLConnectionRegistry:
    """
    Read every row from `external_db` and register a lazy AsyncEngine
    under `resource_name`.

    Contract:
      - The PRIMARY database is touched exactly once: one short-lived
        session, one SELECT. No writes, no extra transactions.
      - External databases are NOT contacted here. create_async_engine()
        only builds the engine object and its pool; the first TCP
        connection happens later, on the first session.execute().
    """
    reg = registry or sql_registry

    # One short-lived session against the PRIMARY database.
    async with alchemy_config.get_session() as session:
        result = await session.execute(select(ExternalDB))
        rows = result.scalars().all()

    for row in rows:
        # EncryptedString decrypts transparently on attribute access.
        try:
            dsn = row.connection_string            
        except Exception as exc:
            if fail_fast:
                raise
            print(
                f"[sql_registry] cannot decrypt DSN for "
                f"'{row.resource_name}': {exc}"
            )
            continue

        if not dsn:
            if fail_fast:
                raise RuntimeError(
                    f"Empty connection_string for '{row.resource_name}'"
                )
            print(
                f"[sql_registry] empty connection_string for "
                f"'{row.resource_name}', skipping"
            )
            continue

        try:
            engine = create_async_engine(dsn)          # lazy, no TCP
            reg.register_engine(row.resource_name, engine)
        except Exception as exc:
            if fail_fast:
                raise
            print(
                f"[sql_registry] cannot create engine for "
                f"'{row.resource_name}': {exc}"
            )

    print(f"[sql_registry] registered: {reg.all_names()}")
    return reg

# session store


session_store_config = { "sessions" : FileStore(path=Path("session_data"), create_directories=True ) }

#session_backend = session_config_b.middleware

# Session backend, store sessions in DB, session ID in cookies. Browser coockie know nothing about user
#session_backend = SQLAlchemyAsyncSessionBackend(
#    config=session_config_b,
    #alchemy_config=alchemy_config,
    #model=WebSession,
#)


#