import pytest
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.plugins.orion_cms.models import CMS_Page_Model

@pytest.mark.asyncio
async def test_create_and_read_page(db_session: AsyncSession):
    """Test direct interaction with the database session."""
    # Arrange
    new_page = CMS_Page_Model(title="New")
    db_session.add(new_page)
    await db_session.flush()  # Push to DB within the active transaction

    # Act
    result = await db_session.execute(select(CMS_Page_Model).where(CMS_Page_Model.title == "New"))
    page = result.scalar_one_or_none()

    # Assert
    assert page is not None
    assert page.title == "New"

#@pytest.mark.asyncio
#async def test_api_endpoint(client: AsyncTestClient):
#    """Test a Litestar endpoint using the overridden dependency session."""
#    response = await client.get("/users")
#    assert response.status_code == 200
#    assert response.json() == [{"id": 1, "name": "Test User"}]
