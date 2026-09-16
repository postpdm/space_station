import pytest

import json

from litestar import Litestar
from litestar.status_codes import HTTP_200_OK
from litestar.testing import AsyncTestClient

from app.core.cage.cage_view import CageController

@pytest.fixture
def app() -> Litestar:
    return Litestar(
        route_handlers=[CageController],
    )


@pytest.mark.asyncio
async def test_user_homepage(app: Litestar) -> None:
    async with AsyncTestClient(app) as client:
        response = await client.get("/cage/fake_user")

    assert response.status_code == HTTP_200_OK

    data = response.json()
    assert data["id"] == '123'
    assert data["userLogin"] == 'fake_domain\\fake_user'
    assert data["userName"] == 'Mr. Fake User jr.'
    assert data["some_key"] == 'some_string'




#@pytest.mark.asyncio
#async def test_api_endpoint(client: AsyncTestClient):
#    """Test a Litestar endpoint using the overridden dependency session."""
#    response = await client.get("/users")
#    assert response.status_code == 200
#    assert response.json() == [{"id": 1, "name": "Test User"}]
