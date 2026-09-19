import pytest
import secrets
from pydantic import SecretStr

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from datetime import datetime, timedelta, timezone

from app.star_fortress.inner_circle.models import ExternalDB
from app.star_fortress.inner_circle.context import db_encryption_key


@pytest.fixture(autouse=True)
def setup_test_encryption_key():
    # generate temporal secret for test usecase
    hex_key = secrets.token_hex(16)
    # set test key
    token = db_encryption_key.set(SecretStr(hex_key))
    yield
    # reset token after use
    db_encryption_key.reset(token)


def _make_external_db(
    resource_name: str = "expires_at_db",
    expires_at=None,
    **overrides,
) -> ExternalDB:
    """Build an ExternalDB instance with sane defaults for these tests."""
    data = dict(
        resource_name=resource_name,
        description="test",
        connection_safe_string="ftp://some_where.galaxy",
        expires_at=expires_at,
    )
    data.update(overrides)
    return ExternalDB(**data)


# =====================================================================
#  WRITE side: @validates('expires_at') + SafeDateTime normalizes invalid -> None
# =====================================================================

@pytest.mark.asyncio
async def test_expires_at_write_aware_datetime(db_session: AsyncSession):
    """Valid tz-aware datetime must be persisted and read back as datetime."""
    # Arrange
    expected_dt = datetime.now(timezone.utc) + timedelta(hours=1)
    new_ec = _make_external_db(expires_at=expected_dt)
    db_session.add(new_ec)
    await db_session.flush()

    # Act
    result = await db_session.execute(
        select(ExternalDB).where(ExternalDB.resource_name == "expires_at_db")
    )
    ec = result.scalar_one_or_none()

    # Assert
    assert ec is not None
    assert isinstance(ec.expires_at, datetime)
    # SQLite/Postgres may drop tzinfo; compare instants, not tzinfo objects
    got = ec.expires_at
    if got.tzinfo is None:
        got = got.replace(tzinfo=timezone.utc)
    assert got == expected_dt


@pytest.mark.asyncio
async def test_expires_at_write_none_is_allowed(db_session: AsyncSession):
    """NULL is a valid value for expires_at."""
    # Arrange
    new_ec = _make_external_db(expires_at=None)
    db_session.add(new_ec)
    await db_session.flush()

    # Act
    result = await db_session.execute(
        select(ExternalDB).where(ExternalDB.resource_name == "expires_at_db")
    )
    ec = result.scalar_one_or_none()

    # Assert
    assert ec is not None
    assert ec.expires_at is None


@pytest.mark.asyncio
async def test_expires_at_write_empty_string_becomes_none(db_session: AsyncSession):
    """Validator must convert '' into None."""
    # Arrange
    new_ec = _make_external_db(expires_at="")
    db_session.add(new_ec)
    await db_session.flush()

    # Act
    result = await db_session.execute(
        select(ExternalDB).where(ExternalDB.resource_name == "expires_at_db")
    )
    ec = result.scalar_one_or_none()

    # Assert
    assert ec is not None
    assert ec.expires_at is None


@pytest.mark.asyncio
async def test_expires_at_write_whitespace_string_becomes_none(db_session: AsyncSession):
    """Whitespace-only string is treated as empty -> None."""
    # Arrange
    new_ec = _make_external_db(expires_at="   \t\n")
    db_session.add(new_ec)
    await db_session.flush()

    # Act
    result = await db_session.execute(
        select(ExternalDB).where(ExternalDB.resource_name == "expires_at_db")
    )
    ec = result.scalar_one_or_none()

    # Assert
    assert ec is not None
    assert ec.expires_at is None


@pytest.mark.asyncio
async def test_expires_at_write_garbage_string_becomes_none(db_session: AsyncSession):
    """
    Non-parsable string is normalized to None by SafeDateTime on the DB side.
    NOTE: must expire the identity map after flush to observe the stored value;
    the in-memory attribute keeps whatever was assigned.
    """
    # Arrange
    new_ec = _make_external_db(expires_at="not-a-date")
    db_session.add(new_ec)
    await db_session.flush()
    db_session.expire_all()  # <-- read the value as it landed in the DB

    # Act
    result = await db_session.execute(
        select(ExternalDB).where(ExternalDB.resource_name == "expires_at_db")
    )
    ec = result.scalar_one_or_none()

    # Assert
    assert ec is not None
    assert ec.expires_at is None
    assert not isinstance(ec.expires_at, str)


@pytest.mark.asyncio
async def test_expires_at_write_wrong_type_becomes_none(db_session: AsyncSession):
    """A non-datetime/non-string value is normalized to None on the DB side."""
    # Arrange
    new_ec = _make_external_db(expires_at=12345)
    db_session.add(new_ec)
    await db_session.flush()
    db_session.expire_all()  # <-- read the value as it landed in the DB

    # Act
    result = await db_session.execute(
        select(ExternalDB).where(ExternalDB.resource_name == "expires_at_db")
    )
    ec = result.scalar_one_or_none()

    # Assert
    assert ec is not None
    assert ec.expires_at is None


@pytest.mark.asyncio
async def test_expires_at_update_valid_to_empty_string(db_session: AsyncSession):
    """Updating a valid value to '' must result in NULL in the DB."""
    # Arrange
    dt = datetime.now(timezone.utc) + timedelta(hours=1)
    new_ec = _make_external_db(expires_at=dt)
    db_session.add(new_ec)
    await db_session.flush()

    # Act
    new_ec.expires_at = ""
    await db_session.flush()
    db_session.expire_all()

    result = await db_session.execute(
        select(ExternalDB).where(ExternalDB.resource_name == "expires_at_db")
    )
    ec = result.scalar_one_or_none()

    # Assert
    assert ec is not None
    assert ec.expires_at is None


@pytest.mark.asyncio
async def test_expires_at_update_valid_to_garbage(db_session: AsyncSession):
    """Updating a valid value to garbage must end up as NULL, not raw string."""
    # Arrange
    dt = datetime.now(timezone.utc) + timedelta(hours=1)
    new_ec = _make_external_db(expires_at=dt)
    db_session.add(new_ec)
    await db_session.flush()

    # Act
    new_ec.expires_at = "totally-broken"
    await db_session.flush()
    db_session.expire_all()

    result = await db_session.execute(
        select(ExternalDB).where(ExternalDB.resource_name == "expires_at_db")
    )
    ec = result.scalar_one_or_none()

    # Assert
    assert ec is not None
    assert ec.expires_at is None
    assert not isinstance(ec.expires_at, str)


# =====================================================================
#  READ side: SafeDateTime normalizes garbage coming FROM the DB -> None
# =====================================================================

@pytest.mark.asyncio
async def test_expires_at_read_null_ok(db_session: AsyncSession):
    """Reading NULL from the DB must give None."""
    # Arrange
    new_ec = _make_external_db(expires_at=None)
    db_session.add(new_ec)
    await db_session.flush()
    db_session.expire_all()

    # Act
    result = await db_session.execute(
        select(ExternalDB).where(ExternalDB.resource_name == "expires_at_db")
    )
    ec = result.scalar_one_or_none()

    # Assert
    assert ec is not None
    assert ec.expires_at is None


@pytest.mark.asyncio
async def test_expires_at_read_garbage_string_becomes_none(db_session: AsyncSession):
    """
    Plant a non-date string directly into the column via raw SQL
    (bypassing the ORM), then read: SafeDateTime must normalize it to None,
    never expose the raw string.
    """
    # Arrange: create a row with NULL expires_at first
    new_ec = _make_external_db(expires_at=None)
    db_session.add(new_ec)
    await db_session.flush()

    # Act: raw UPDATE bypasses ORM / SafeDateTime on write side
    await db_session.execute(
        text("UPDATE external_db SET expires_at = :v WHERE resource_name = :rn"),
        {"v": "totally-broken", "rn": "expires_at_db"},
    )
    await db_session.flush()
    db_session.expire_all()

    result = await db_session.execute(
        select(ExternalDB).where(ExternalDB.resource_name == "expires_at_db")
    )
    ec = result.scalar_one_or_none()

    # Assert: garbage from DB is normalized, not leaked as a raw string
    assert ec is not None
    assert ec.expires_at is None
    assert not isinstance(ec.expires_at, str)


@pytest.mark.asyncio
async def test_expires_at_read_valid_roundtrip(db_session: AsyncSession):
    """A valid value must survive a flush + re-read."""
    # Arrange
    dt = datetime.now(timezone.utc) + timedelta(days=1)
    new_ec = _make_external_db(expires_at=dt)
    db_session.add(new_ec)
    await db_session.flush()
    db_session.expire_all()

    # Act
    result = await db_session.execute(
        select(ExternalDB).where(ExternalDB.resource_name == "expires_at_db")
    )
    ec = result.scalar_one_or_none()

    # Assert
    assert ec is not None
    assert isinstance(ec.expires_at, datetime)
    got = ec.expires_at
    if got.tzinfo is None:
        got = got.replace(tzinfo=timezone.utc)
    assert got == dt


# =====================================================================
#  is_expired property
# =====================================================================

def test_is_expired_none_is_false():
    """NULL expires_at means 'never expires'."""
    ec = _make_external_db(expires_at=None)
    assert ec.is_expired is False


def test_is_expired_future_is_false():
    """A future datetime is not expired."""
    ec = _make_external_db(
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    assert ec.is_expired is False


def test_is_expired_past_is_true():
    """A past datetime is expired."""
    ec = _make_external_db(
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    assert ec.is_expired is True


def test_is_expired_boundary_uses_ge():
    """`datetime.now() >= expires_at` - exactly 'now' is already expired."""
    ec = _make_external_db(
        expires_at=datetime.now(timezone.utc) - timedelta(microseconds=1)
    )
    assert ec.is_expired is True