import pytest
import pytest_asyncio
from litestar import Litestar
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool
from advanced_alchemy.extensions.litestar import base

from app.plugins.orion_cms.models import CMS_Page_Model

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
