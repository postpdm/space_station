import pytest
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from datetime import date

from app.plugins.orion_cms.models import CMS_Page_Model, CMS_Tree_Model
from app.plugins.orion_cms.parsers import execute_orion_manusctript

@pytest.mark.asyncio
async def test_create_tree(db_session: AsyncSession):
    """Test direct interaction with the database session."""
    # Arrange
    new_tree = CMS_Tree_Model( title="Volume1" )
    db_session.add(new_tree)
    await db_session.flush()  # Push to DB within the active transaction

    # Act
    result = await db_session.execute(select(CMS_Tree_Model).where(CMS_Tree_Model.title == "Volume1"))
    tree = result.scalar_one_or_none()

    # Assert
    assert tree is not None
    assert tree.title == "Volume1"

@pytest.mark.asyncio
async def test_create_and_read_page(db_session: AsyncSession):
    """Test direct interaction with the database session."""
    # Arrange
    new_tree = CMS_Tree_Model( title="Volume1" )
    db_session.add(new_tree)
    await db_session.flush()  # Push to DB within the active transaction

    new_page = CMS_Page_Model(tree_id = new_tree.id, title="New")
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

    code = ': abra-cadabra'
    component_str = await execute_orion_manusctript( code, db_session )

    assert component_str == 'Unknown command: abra-cadabra'

@pytest.mark.asyncio
async def test_sql_parser_validate_sql(db_session: AsyncSession):
    """Test Orion manuscript parser."""

    code = ': sql\n DROP DATABASE'
    component_str = await execute_orion_manusctript( code, db_session )
    assert component_str == 'Fail to parse and execute SQL'

@pytest.mark.asyncio
async def test_sql_parser_sql_command_show_html_table(db_session: AsyncSession):
    """Test Orion manuscript parser with sql command."""
    # Arrange
    new_tree = CMS_Tree_Model( title="Volume1" )
    db_session.add(new_tree)
    await db_session.flush()  # Push to DB within the active transaction

    new_page = CMS_Page_Model( tree_id = new_tree.id, title="New page to sql test")
    db_session.add(new_page)
    await db_session.flush()  # Push to DB within the active transaction

    code = ': sql \n' + 'select count(id) AS C from cms_page \n' + ': show table'
    component_str = await execute_orion_manusctript( code, db_session )
    assert component_str == '<table border="2"><thead><tr><th>C</th></tr></thead><tbody><tr><td>1</td></tr></tbody></table>'

@pytest.mark.asyncio
async def test_show_html_table_forgot_sql(db_session: AsyncSession):
    """Test Orion manuscript parser without sql command."""
    code = ': show table'
    component_str = await execute_orion_manusctript( code, db_session )
    assert component_str == 'No dataset to show'

@pytest.mark.asyncio
async def test_show_graph_forgot_sql(db_session: AsyncSession):
    """Test Orion manuscript parser without sql command."""
    code = ': show mermaid'
    component_str = await execute_orion_manusctript( code, db_session )
    assert component_str == 'No dataset to show'


MERMAID_STR = """
pie title Pie chart
{% for i in dataset %}
    "{{i.1}}" : {{i.0}}
{% endfor %}
"""

@pytest.mark.asyncio
async def test_sql_parser_sql_command_show_mermaid_graph(db_session: AsyncSession):
    """Test Orion manuscript parser with sql command."""
    # Arrange
    new_tree = CMS_Tree_Model( title="Volume1" )
    db_session.add(new_tree)

    await db_session.flush()  # Push to DB within the active transaction

    new_page = CMS_Page_Model( title="New page to sql test", tree_id = new_tree.id )
    db_session.add(new_page)
    await db_session.flush()  # Push to DB within the active transaction

    code = ':sql \n select count(id), date(created_at) from cms_page group by date(created_at) \n' + ': show mermaid \n' + MERMAID_STR

    component_str = await execute_orion_manusctript( code, db_session )

    # use today
    expected = f"""``` mermaid
pie title Pie chart\n
    "{date.today()}" : 1\n\n```"""
    
    assert component_str == expected


#@pytest.mark.asyncio
#async def test_api_endpoint(client: AsyncTestClient):
#    """Test a Litestar endpoint using the overridden dependency session."""
#    response = await client.get("/users")
#    assert response.status_code == 200
#    assert response.json() == [{"id": 1, "name": "Test User"}]
