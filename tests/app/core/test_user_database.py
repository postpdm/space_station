import pytest
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from sqlalchemy.exc import IntegrityError

#from datetime import date

from app.core.core_models import User

@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Test direct interaction with the database session."""
    # Arrange
    new_user = User( user_login="TEST_USER", user_name="Mr. Test User" )
    db_session.add(new_user)
    await db_session.flush()  # Push to DB within the active transaction

    # Act
    result = await db_session.execute(select(User).where(User.user_login=="TEST_USER"))
    user = result.scalar_one_or_none()

    # Assert
    assert user is not None
    assert user.user_login == "TEST_USER"
    assert user.user_name == "Mr. Test User"

@pytest.mark.asyncio
async def test_create_NO_unique_user(db_session: AsyncSession):
    """Test direct interaction with the database session."""
    # Arrange
    new_user = User( user_login="TEST_USER", user_name="Mr. Test User" )
    db_session.add(new_user)
    await db_session.flush()  # Push to DB within the active transaction

    # try to create another user with the same LOGIN
    second_user = User( user_login="TEST_USER", user_name="Mr. SECOND User" )
    db_session.add(second_user)

    with pytest.raises(IntegrityError):
        await db_session.flush()  # Push to DB within the active transaction
