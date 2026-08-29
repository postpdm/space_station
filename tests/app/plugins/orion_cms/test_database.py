import pytest
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.plugins.orion_cms.models import CMS_Page_Model
from app.plugins.orion_cms.parsers import execute_orion_manusctript

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

@pytest.mark.asyncio
async def test_sql_parser_unknown_command(db_session: AsyncSession):
    """Test Orion manuscript parser."""

    code = 'abra-cadabra'
    component_str = await execute_orion_manusctript( code, db_session )
    
    assert component_str == 'Unknown command "abra-cadabra"'

@pytest.mark.asyncio
async def test_sql_parser_sql_command(db_session: AsyncSession):
    """Test Orion manuscript parser with sql command."""
    # Arrange
    new_page = CMS_Page_Model(title="New page to sql test")
    db_session.add(new_page)
    await db_session.flush()  # Push to DB within the active transaction

    code = 'select count(id) AS C from cms_page \n' + 'show table'
    component_str = await execute_orion_manusctript( code, db_session )
    assert component_str == '<table border="2"><thead><tr><th>C</th></tr></thead><tbody><tr><td>1</td></tr></tbody></table>'


#@pytest.mark.asyncio
#async def test_api_endpoint(client: AsyncTestClient):
#    """Test a Litestar endpoint using the overridden dependency session."""
#    response = await client.get("/users")
#    assert response.status_code == 200
#    assert response.json() == [{"id": 1, "name": "Test User"}]
