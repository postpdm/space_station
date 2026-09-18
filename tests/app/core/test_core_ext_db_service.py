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
async def test_ext_db_connection_do_not_send_pw_in_url():
    """Test connect to wrong external db."""
    url_with_pw = "UUUUUUU://user:pass@127.0.0.1:9999/wrong_db"

    success, message = await check_ext_db_connection(url_with_pw)

    print( message )

    assert success is False
    assert message == "❌ Connection error: Database URL must not contain a password. " + "Pass it via the 'arg_password' argument instead."


"""Tests for `app.core.core_ext_db_service.check_ext_db_connection`.

The function under test never raises on configuration or connection
problems - every failure is returned as `(False, "<message>")`.
"""

from unittest.mock import AsyncMock, MagicMock, patch



# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Patch target must point to the symbol at its import site in the service module.
CONFIG_PATCH_TARGET = "app.core.core_ext_db_service.SQLAlchemyAsyncConfig"

BASE_URL = "postgresql+asyncpg://user@localhost:5432/db"
BASE_URL_WITH_PASSWORD = "postgresql+asyncpg://user:secret@localhost:5432/db"
BASE_URL_WITH_ENCODED_PASSWORD = "postgresql+asyncpg://user:p%40ss@localhost:5432/db"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_engine():
    """Build a mock async engine whose connect() yields an async context manager."""
    conn = AsyncMock()
    conn.__aenter__.return_value = conn
    conn.__aexit__.return_value = None

    engine = MagicMock()
    engine.connect.return_value = conn
    engine.dispose = AsyncMock()
    return engine


@pytest.fixture
def mock_config(mock_engine):
    """Build a mock SQLAlchemyAsyncConfig whose get_engine() returns mock_engine."""
    config = MagicMock()
    config.get_engine.return_value = mock_engine
    return config


# ---------------------------------------------------------------------------
# Password inside the URL is rejected and reported as (False, ...)
# ---------------------------------------------------------------------------

class TestPasswordInUrlRejected:

    @pytest.mark.asyncio
    async def test_plain_password_in_url_returns_false(self):
        ok, msg = await check_ext_db_connection(BASE_URL_WITH_PASSWORD)
        assert ok is False
        assert "must not contain a password" in msg

    @pytest.mark.asyncio
    async def test_percent_encoded_password_in_url_returns_false(self):
        # '%40' is the encoded form of '@' - still a password in the URL.
        ok, msg = await check_ext_db_connection(BASE_URL_WITH_ENCODED_PASSWORD)
        assert ok is False
        assert "must not contain a password" in msg

    @pytest.mark.asyncio
    async def test_password_in_url_returns_false_even_with_arg_password(self):
        # Providing `arg_password` must not mask a password already in the URL.
        ok, msg = await check_ext_db_connection(
            BASE_URL_WITH_PASSWORD, arg_password="other"
        )
        assert ok is False
        assert "must not contain a password" in msg

    @pytest.mark.asyncio
    async def test_no_connection_attempted_when_url_has_password(self, mock_config):
        # The config must never be instantiated if the URL is rejected.
        with patch(CONFIG_PATCH_TARGET, return_value=mock_config) as MockCfg:
            ok, _ = await check_ext_db_connection(BASE_URL_WITH_PASSWORD)
        assert ok is False
        MockCfg.assert_not_called()


# ---------------------------------------------------------------------------
# Successful connection
# ---------------------------------------------------------------------------

class TestConnectionSuccess:

    @pytest.mark.asyncio
    async def test_connect_without_password(self, mock_config):
        with patch(CONFIG_PATCH_TARGET, return_value=mock_config):
            ok, msg = await check_ext_db_connection(BASE_URL)
        assert ok is True
        assert "successfully" in msg

    @pytest.mark.asyncio
    async def test_connect_with_password(self, mock_config):
        with patch(CONFIG_PATCH_TARGET, return_value=mock_config) as MockCfg:
            ok, _ = await check_ext_db_connection(BASE_URL, arg_password="hunter2")

        assert ok is True
        connection_string = MockCfg.call_args.kwargs["connection_string"]
        assert ":hunter2@" in connection_string

    @pytest.mark.asyncio
    async def test_password_arg_is_optional(self, mock_config):
        with patch(CONFIG_PATCH_TARGET, return_value=mock_config):
            ok, _ = await check_ext_db_connection(BASE_URL, arg_password=None)
        assert ok is True


# ---------------------------------------------------------------------------
# Special characters in the password are URL-encoded
# ---------------------------------------------------------------------------

class TestPasswordSpecialCharacterEncoding:

    @pytest.mark.parametrize(
        "raw_password, encoded_fragment",
        [
            ("pass@word",  "pass%40word"),   # '@' -> %40
            ("pass?word",  "pass%3Fword"),   # '?' -> %3F
            ("pass|word",  "pass%7Cword"),   # '|' -> %7C
            ("pass;word",  "pass%3Bword"),   # ';' -> %3B
            ("pass:word",  "pass%3Aword"),   # ':' -> %3A
            ("pass/word",  "pass%2Fword"),   # '/' -> %2F
            ("pass#word",  "pass%23word"),   # '#' -> %23
            ("pass&word",  "pass%26word"),   # '&' -> %26
            ("pass\\word", "pass%5Cword"),   # '\' -> %5C
        ],
    )
    @pytest.mark.asyncio
    async def test_special_char_is_encoded(
        self, mock_config, raw_password, encoded_fragment
    ):
        with patch(CONFIG_PATCH_TARGET, return_value=mock_config) as MockCfg:
            ok, _ = await check_ext_db_connection(BASE_URL, arg_password=raw_password)

        assert ok is True
        connection_string = MockCfg.call_args.kwargs["connection_string"]
        assert encoded_fragment in connection_string
        # The raw password must not leak into the rendered URL.
        assert raw_password not in connection_string

    @pytest.mark.asyncio
    async def test_multiple_special_chars_are_encoded(self, mock_config):
        raw_password = "p@ss:w|rd;?/"
        with patch(CONFIG_PATCH_TARGET, return_value=mock_config) as MockCfg:
            ok, _ = await check_ext_db_connection(BASE_URL, arg_password=raw_password)

        assert ok is True
        connection_string = MockCfg.call_args.kwargs["connection_string"]
        for encoded in ("p%40ss", "%3A", "%7C", "%3B", "%3F", "%2F"):
            assert encoded in connection_string
        assert raw_password not in connection_string

    @pytest.mark.asyncio
    async def test_space_is_not_encoded_by_sqlalchemy(self, mock_config):
        # SQLAlchemy's URL.render_as_string() uses urllib.parse.quote with
        # safe=" +", so space and '+' are intentionally left unencoded.
        # This test pins that behaviour so future upgrades are noticed.
        with patch(CONFIG_PATCH_TARGET, return_value=mock_config) as MockCfg:
            ok, _ = await check_ext_db_connection(BASE_URL, arg_password="pass word")

        assert ok is True
        connection_string = MockCfg.call_args.kwargs["connection_string"]
        assert "pass word@" in connection_string

    @pytest.mark.asyncio
    async def test_plus_is_not_encoded_by_sqlalchemy(self, mock_config):
        # Same rationale as `test_space_is_not_encoded_by_sqlalchemy`.
        with patch(CONFIG_PATCH_TARGET, return_value=mock_config) as MockCfg:
            ok, _ = await check_ext_db_connection(BASE_URL, arg_password="pass+word")

        assert ok is True
        connection_string = MockCfg.call_args.kwargs["connection_string"]
        assert "pass+word@" in connection_string


# ---------------------------------------------------------------------------
# Connection errors are returned as (False, message) and the engine is disposed
# ---------------------------------------------------------------------------

class TestConnectionErrors:

    @pytest.mark.asyncio
    async def test_connection_error_returns_false_tuple(self, mock_config, mock_engine):
        mock_engine.connect.return_value.__aenter__.side_effect = OSError("boom")
        with patch(CONFIG_PATCH_TARGET, return_value=mock_config):
            ok, msg = await check_ext_db_connection(BASE_URL)
        assert ok is False
        assert "Connection error" in msg
        assert "boom" in msg

    @pytest.mark.asyncio
    async def test_connection_error_message_has_cross_mark_prefix(
        self, mock_config, mock_engine
    ):
        mock_engine.connect.return_value.__aenter__.side_effect = OSError("boom")
        with patch(CONFIG_PATCH_TARGET, return_value=mock_config):
            _, msg = await check_ext_db_connection(BASE_URL)
        assert msg.startswith("❌")

    @pytest.mark.asyncio
    async def test_engine_disposed_on_success(self, mock_config, mock_engine):
        with patch(CONFIG_PATCH_TARGET, return_value=mock_config):
            await check_ext_db_connection(BASE_URL)
        mock_engine.dispose.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_engine_disposed_on_failure(self, mock_config, mock_engine):
        mock_engine.connect.return_value.__aenter__.side_effect = OSError("boom")
        with patch(CONFIG_PATCH_TARGET, return_value=mock_config):
            await check_ext_db_connection(BASE_URL)
        mock_engine.dispose.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_no_engine_created_when_config_raises(self):
        # If SQLAlchemyAsyncConfig itself blows up, dispose() must not be called
        # because there is no engine yet.
        with patch(
            CONFIG_PATCH_TARGET, side_effect=RuntimeError("config boom")
        ) as MockCfg:
            ok, msg = await check_ext_db_connection(BASE_URL)

        assert ok is False
        assert "config boom" in msg
        MockCfg.assert_called_once()


# ---------------------------------------------------------------------------
# Success message shape
# ---------------------------------------------------------------------------

class TestSuccessMessage:

    @pytest.mark.asyncio
    async def test_success_message_has_check_mark_prefix(self, mock_config):
        with patch(CONFIG_PATCH_TARGET, return_value=mock_config):
            ok, msg = await check_ext_db_connection(BASE_URL)
        assert ok is True
        assert msg.startswith("✅")