import pytest

import secrets

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from sqlalchemy.exc import IntegrityError

from datetime import datetime, date, timezone

from app.core.core_models import User
from app.star_fortress.inner_circle.models import ExternalCredential
from app.star_fortress.inner_circle.context import db_encryption_key

@pytest.fixture(autouse=True)
def setup_test_encryption_key():
    # generate temporal secret for test usecase
    hex_key = secrets.token_hex(16)
    # set test key
    token = db_encryption_key.set( hex_key )
    yield
    # reset token after use
    db_encryption_key.reset(token)
    
@pytest.mark.asyncio
async def test_externalcredential_model(db_session: AsyncSession):
    """Test direct interaction with the database session."""
    # Arrange
    expected_res_name = "my_secret_db"
    expected_url = "ftp://some_where.galaxy"
    new_ec = ExternalCredential( resource_name = expected_res_name, api_key_or_connection_string = expected_url, expires_at = datetime.now( timezone.utc ) )
    db_session.add(new_ec)
    await db_session.flush()  # Push to DB within the active transaction

    # Act
    result = await db_session.execute(select(ExternalCredential).where(ExternalCredential.resource_name == "my_secret_db" ) )
    ec = result.scalar_one_or_none()

    # Assert
    assert ec is not None
    assert ec.resource_name == expected_res_name
    assert ec.api_key_or_connection_string == expected_url