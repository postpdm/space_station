import pytest

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.core_ext_db_service import check_ext_db_connection

@pytest.mark.asyncio
async def test_ext_db_connection_success():
    """Test connect to right external db, for SQLite memory sample."""
    # Arrange

    valid_url = "sqlite+aiosqlite:///:memory:"

    success, message = await check_ext_db_connection(valid_url)

    assert success is True
    assert message == "✅ Database connection established successfully!"

@pytest.mark.asyncio
async def test_ext_db_connection_wrong_port_error():
    """Test connect to wrong external db."""
    invalid_url = "UUUUUUU://user:pass@127.0.0.1:9999/wrong_db"

    success, message = await check_ext_db_connection(invalid_url)

    assert success is False
    assert message == "❌ Connection error: Can't load plugin: sqlalchemy.dialects:UUUUUUU"