import pytest

import secrets
from pydantic import SecretStr

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from sqlalchemy.exc import IntegrityError

from datetime import datetime, date, timezone

from app.star_fortress.inner_circle.models import ExternalDB, SourceType
from app.star_fortress.inner_circle.context import db_encryption_key

@pytest.fixture(autouse=True)
def setup_test_encryption_key():
    # generate temporal secret for test usecase
    hex_key = secrets.token_hex(16)
    # set test key
    token = db_encryption_key.set( SecretStr( hex_key ) )
    yield
    # reset token after use
    db_encryption_key.reset(token)

@pytest.mark.asyncio
async def test_external_datasource_good(db_session: AsyncSession):
    """Test direct interaction with the database session."""
    # Arrange
    expected_res_name = "my_secret_db"
    expected_url = "ftp://some_where.galaxy"
    expected_datasource_type = SourceType.SQL.value
    
    new_ec = ExternalDB( resource_name = expected_res_name, description='test', connection_safe_string = expected_url )
    db_session.add(new_ec)
    await db_session.flush()  # Push to DB within the active transaction

    # Act
    result = await db_session.execute(select(ExternalDB).where(ExternalDB.resource_name == "my_secret_db" ) )
    ec = result.scalar_one_or_none()

    # Assert
    assert ec is not None
    assert ec.resource_name == expected_res_name
    assert ec.connection_safe_string == expected_url
    assert ec.source_type == expected_datasource_type

#