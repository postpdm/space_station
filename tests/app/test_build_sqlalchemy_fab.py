"""Tests for build_sqlalchemy_fab: reading external_db, never raising."""
from unittest.mock import MagicMock

import pytest

from app.core import core_config


# ----------------------------------------------------------------------
# Fixtures local to this file: patches for alchemy_config and the
# engine factory. They are only useful for fab tests, so keep them here.
# ----------------------------------------------------------------------
@pytest.fixture
def patch_alchemy(monkeypatch, make_alchemy_config):
    def _patch(rows=None, raise_on_session=None):
        monkeypatch.setattr(
            core_config,
            "alchemy_config",
            make_alchemy_config(rows=rows, raise_on_session=raise_on_session),
        )
    return _patch


@pytest.fixture
def patch_engine_factory(monkeypatch):
    """Replace create_async_engine with a recorder; returns the list."""
    captured: list[str] = []

    def fake_create(dsn, *args, **kwargs):
        captured.append(dsn)
        return MagicMock()

    monkeypatch.setattr(core_config, "create_async_engine", fake_create)
    return captured


# ----------------------------------------------------------------------
# Happy path
# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_fab_registers_all_good_rows(
    registry,
    patch_alchemy,
    patch_engine_factory,
    make_external_row,
    capsys,
) -> None:
    rows = [
        make_external_row("report_database", "postgresql+asyncpg://h/r", None ),
        make_external_row("audit_db", "postgresql+asyncpg://h/a", None ),
    ]
    patch_alchemy(rows=rows)

    result = await core_config.build_sqlalchemy_fab(registry=registry)

    assert result is registry
    assert set(registry.all_names()) == {"report_database", "audit_db"}
    assert patch_engine_factory == [
        "postgresql+asyncpg://h/r",
        "postgresql+asyncpg://h/a",
    ]
    assert "registered connections" in capsys.readouterr().out


# ----------------------------------------------------------------------
# Empty external_db
# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_fab_empty_db_registers_nothing(
    registry, patch_alchemy, patch_engine_factory, capsys
) -> None:
    patch_alchemy(rows=[])

    await core_config.build_sqlalchemy_fab(registry=registry)

    assert registry.all_names() == []
    assert "no external connections registered" in capsys.readouterr().out


# ----------------------------------------------------------------------
# Broken rows are skipped, not fatal
# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_fab_skips_invalid_url(
    registry, patch_alchemy, patch_engine_factory, make_external_row, capsys
) -> None:
    rows = [
        make_external_row("good", "postgresql+asyncpg://h/g", None ),
        make_external_row("fail", "FAIL:::::", None ),
    ]
    patch_alchemy(rows=rows)

    await core_config.build_sqlalchemy_fab(registry=registry)

    assert registry.has("good")
    assert not registry.has("fail")
    out = capsys.readouterr().out
    assert "'fail'" in out
    assert "cannot decrypt DSN" in out


@pytest.mark.asyncio
async def test_fab_skips_empty_connection_string(
    registry, patch_alchemy, patch_engine_factory, make_external_row, capsys
) -> None:
    patch_alchemy(rows=[make_external_row("empty", "   ", None)])

    await core_config.build_sqlalchemy_fab(registry=registry)

    assert registry.all_names() == []
    assert "empty connection_string" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_fab_skips_when_decrypt_fails(
    registry, patch_alchemy, patch_engine_factory, capsys
) -> None:
    class BrokenRow:
        resource_name = "crypted"

        @property
        def connection_safe_string(self):
            raise RuntimeError("no key")

    patch_alchemy(rows=[BrokenRow()])

    await core_config.build_sqlalchemy_fab(registry=registry)

    assert registry.all_names() == []
    out = capsys.readouterr().out
    print( out )
    assert "empty connection_string" in out


@pytest.mark.asyncio
async def test_fab_skips_when_engine_creation_fails(
    registry, patch_alchemy, make_external_row, monkeypatch, capsys
) -> None:
    patch_alchemy(rows=[make_external_row("bad-dialect", "nosuchdialect://h/d", None )])

    def fake_create(dsn, *a, **kw):
        raise ModuleNotFoundError("no driver")

    monkeypatch.setattr(core_config, "create_async_engine", fake_create)

    await core_config.build_sqlalchemy_fab(registry=registry)

    assert registry.all_names() == []
    assert "cannot create engine" in capsys.readouterr().out


# ----------------------------------------------------------------------
# Main DB unavailable
# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_fab_main_db_unavailable_logs_and_returns(
    registry, patch_alchemy, patch_engine_factory, capsys, plain_out
) -> None:
    patch_alchemy(raise_on_session=RuntimeError("connection refused"))

    result = await core_config.build_sqlalchemy_fab(registry=registry)

    assert result is registry
    assert registry.all_names() == []

    out = plain_out(capsys.readouterr().out)
    assert "FATAL" in out
    assert "connection refused" in out

# ----------------------------------------------------------------------
# Duplicate names
# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_fab_duplicate_name_overwrites_and_warns(
    registry, patch_alchemy, patch_engine_factory, make_external_row, capsys
) -> None:
    rows = [
        make_external_row("dup", "postgresql+asyncpg://h/1", None ),
        make_external_row("dup", "postgresql+asyncpg://h/2", None ),
    ]
    patch_alchemy(rows=rows)

    await core_config.build_sqlalchemy_fab(registry=registry)

    assert registry.has("dup")
    assert "duplicate resource_name" in capsys.readouterr().out


# ----------------------------------------------------------------------
# Default registry when none is passed
# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_fab_uses_default_registry(
    patch_alchemy, patch_engine_factory, make_external_row
) -> None:
    patch_alchemy(rows=[make_external_row("x", "postgresql+asyncpg://h/x", "123" )])

    core_config.sql_registry._connections.clear()
    result = await core_config.build_sqlalchemy_fab()

    assert result is core_config.sql_registry
    assert result.has("x")