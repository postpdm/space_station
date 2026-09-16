from pathlib import Path

from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin

from advanced_alchemy.extensions.litestar import AsyncSessionConfig
#from advanced_alchemy.extensions.litestar.session import SQLAlchemyAsyncSessionBackend
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

from litestar.middleware.session.server_side import ServerSideSessionConfig

from litestar.stores.file import FileStore

"""Core configuration: DB plugin, sessions, and SQL connection registry."""
from litestar.plugins.sqlalchemy import SQLAlchemyPlugin, SQLAlchemySyncConfig

from rich import print as rich_p

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
) -> SQLConnectionRegistry:
    """
    Read external_db and register a lazy AsyncEngine per resource_name.
    Broken rows are logged to the console (in red) and skipped; the
    function never raises, so the application can still start and let
    the admin fix the data via the UI.
    """
    reg = registry or sql_registry

    # One short-lived session against the PRIMARY database.
    try:
        async with alchemy_config.get_session() as session:
            result = await session.execute(select(ExternalDB))
            rows = result.scalars().all()
    except Exception as exc:
        rich_p(
            f"[red][sql_registry] FATAL: cannot read external_db "
            f"from primary DB: {type(exc).__name__}: {exc}[/red]"
        )
        return reg

    for row in rows:
        name = row.resource_name

        # Decrypt DSN.
        try:
            dsn = row.connection_string
        except Exception as exc:
            rich_p(
                f"[red][sql_registry] '{name}': cannot decrypt DSN: "
                f"{type(exc).__name__}: {exc}[/red]"
            )
            continue

        # Reject empty values.
        if not dsn or not dsn.strip():
            rich_p(f"[red][sql_registry] '{name}': empty connection_string[/red]")
            continue

        # Validate URL syntax (pure parser, no side effects).
        try:
            make_url(dsn)
        except ArgumentError as exc:
            rich_p(
                f"[red][sql_registry] '{name}': invalid URL syntax "
                f"({dsn!r}): {exc}[/red]"
            )
            continue

        # Build the engine. Still lazy: no TCP connection here.
        try:
            engine = create_async_engine(dsn)
        except (ArgumentError, ModuleNotFoundError, ImportError) as exc:
            rich_p(
                f"[red][sql_registry] '{name}': cannot create engine: "
                f"{type(exc).__name__}: {exc}[/red]"
            )
            continue

        if reg.has(name):
            rich_p(
                f"[yellow][sql_registry] '{name}': duplicate "
                f"resource_name, overwriting[/yellow]"
            )

        reg.register_engine(name, engine)

    if reg.all_names():
        rich_p(
            f"[sql_registry] registered connections: "
            f"{reg.all_names()}"
        )
    else:
        rich_p("[red][sql_registry] no external connections registered[/red]")

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