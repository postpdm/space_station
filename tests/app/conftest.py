"""Shared fixtures and plugin classes for application-level tests."""
import pytest
import pytest_asyncio
from litestar import Litestar
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool
from advanced_alchemy.extensions.litestar import base

from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from space_station_stc.hull.plugin_abc.sql_bundle import SQLConnectionBundle
from space_station_stc.hull.plugin_abc.sql_registry import SQLConnectionRegistry
from space_station_stc.hull.plugin_abc.abc_plugin import BasePlugin

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Setup the async SQLite in-memory engine
# StaticPool is required to keep the same database connection alive across tests
@pytest_asyncio.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # import my_project.models

    # init metadata из advanced_alchemy
    async with engine.begin() as conn:
        await conn.run_sync(base.orm_registry.metadata.create_all)

    yield engine
    await engine.dispose()

# Setup the database session with transactional isolation (auto-rollback)
@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncSession:
    async_session_factory = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_factory() as session:
        async with session.begin():  # Start a transaction block
            yield session
            await session.rollback()  # Rollback all changes after the test ends

# Setup the Litestar app fixture with dependency injection override
@pytest.fixture
def app(db_session: AsyncSession) -> Litestar:
    from litestar import get

 #   # Example endpoint that requires a database session
 #   @get("/users")
 #   async def get_users(db: AsyncSession) -> list[dict]:
 #       return [{"id": 1, "name": "Test User"}]

    # Define an async callable to avoid LitestarWarning (implicit sync_to_thread)
    async def get_db_session() -> AsyncSession:
        return db_session

    return Litestar(
        #route_handlers=[get_users],
        route_handlers=[],
        dependencies={"db": get_db_session}
    )

# Setup the Litestar async test client
@pytest_asyncio.fixture
async def client(app: Litestar) -> AsyncTestClient:
    async with AsyncTestClient(app=app) as async_client:
        yield async_client


# ----------------------------------------------------------------------
# Canonical plugin classes reused across tests.
# ----------------------------------------------------------------------
class NoSqlPlugin(BasePlugin):
    """Plugin with no SQL needs at all."""
    fplugin_id = UUID("00000000-0000-0000-0000-000000000001")
    fuser_title = "NoSQL"
    fuser_description = "Plugin without SQL"


class SqlPlugin(BasePlugin):
    """Plugin declaring a single known connection."""
    fplugin_id = UUID("00000000-0000-0000-0000-000000000002")
    fuser_title = "SQL"
    fuser_description = "Plugin with one SQL connection"
    fsql_connections = ["report_database"]


class GhostSqlPlugin(BasePlugin):
    """Plugin declaring a connection the core does not provide."""
    fplugin_id = UUID("00000000-0000-0000-0000-000000000003")
    fuser_title = "Ghost"
    fuser_description = "Plugin asking for a non-existent connection"
    fsql_connections = ["ghost_db"]


class MultiSqlPlugin(BasePlugin):
    """Plugin declaring two connections, used in multi-name tests."""
    fplugin_id = UUID("00000000-0000-0000-0000-000000000004")
    fuser_title = "Multi"
    fuser_description = "Plugin with two SQL connections"
    fsql_connections = ["report_database", "audit_db"]


# ----------------------------------------------------------------------
# Dynamic plugin class factory - for tests that need a unique UUID
# on every call (dedup tests, iteration over many modules, etc.).
# ----------------------------------------------------------------------
@pytest.fixture
def make_plugin_class():
    def _make(
        name: str,
        plugin_id: UUID | None = None,
        sql: list[str] | None = None,
    ) -> type[BasePlugin]:
        ns: dict = {
            "fplugin_id": plugin_id or UUID(int=0).__class__(  # fresh uuid4
                # use uuid4() from stdlib
                __import__("uuid").uuid4().int,
                version=4,
            ),
            "fuser_title": name,
            "fuser_description": f"{name} description",
        }
        if sql is not None:
            ns["fsql_connections"] = sql
        return type(name, (BasePlugin,), ns)

    return _make


# ----------------------------------------------------------------------
# Fake engine / sessionmaker / bundle
# ----------------------------------------------------------------------
@pytest.fixture
def fake_engine() -> MagicMock:
    engine = MagicMock(spec=AsyncEngine)
    engine.dispose = AsyncMock()
    return engine


@pytest.fixture
def fake_sessionmaker() -> MagicMock:
    return MagicMock(spec=async_sessionmaker)


@pytest.fixture
def fake_bundle(fake_engine, fake_sessionmaker) -> SQLConnectionBundle:
    return SQLConnectionBundle(engine=fake_engine, sessionmaker=fake_sessionmaker)


@pytest.fixture
def registry() -> SQLConnectionRegistry:
    return SQLConnectionRegistry()


@pytest.fixture
def registry_with_report_db(registry, fake_bundle) -> SQLConnectionRegistry:
    registry.register_bundle("report_database", fake_bundle)
    return registry


# ----------------------------------------------------------------------
# Fake alchemy_config and rows
# ----------------------------------------------------------------------
class FakeSession:
    """Session stub returning a preset list of rows from execute()."""
    def __init__(self, rows):
        self._rows = rows

    async def execute(self, stmt):
        class _Result:
            def __init__(self, rows): self._rows = rows
            def scalars(self): return self
            def all(self): return self._rows
        return _Result(self._rows)

    async def __aenter__(self): return self
    async def __aexit__(self, *a): return False


class FakeAlchemyConfig:
    """Minimal stand-in for SQLAlchemyAsyncConfig.get_session()."""
    def __init__(self, rows=None, raise_on_session: Exception | None = None):
        self._rows = rows or []
        self._raise = raise_on_session

    def get_session(self):
        if self._raise is not None:
            raise self._raise
        return FakeSession(self._rows)


class FakeExternalDBRow:
    """Row-shaped object imitating ExternalDB model attributes."""
    def __init__(self, name: str, dsn: str | None):
        self.resource_name = name
        self.connection_string = dsn


@pytest.fixture
def make_alchemy_config():
    def _make(rows=None, raise_on_session=None):
        return FakeAlchemyConfig(rows=rows, raise_on_session=raise_on_session)
    return _make


@pytest.fixture
def make_external_row():
    def _make(name: str, dsn: str | None):
        return FakeExternalDBRow(name=name, dsn=dsn)
    return _make
