"""End-to-end test of the on_startup hook contract."""
import pytest

from tests.app.conftest import GhostSqlPlugin, SqlPlugin


@pytest.mark.asyncio
async def test_startup_hook_distributes_bundles(
    registry, fake_bundle, make_plugin_instance, capsys
):
    """
    Reproduce the body of app.init_plugin_sql_connections without
    importing app.py (which has side effects):

      1) fab fills the registry;
      2) bundles are distributed to plugins according to fsql_connections;
      3) missing names are reported via check_sql_connections.
    """
    async def fake_fab(*, registry=None):
        registry.register_bundle("report_database", fake_bundle)
        return registry

    plugins = [ make_plugin_instance(SqlPlugin),
                make_plugin_instance(GhostSqlPlugin)]
           
    async def init_hook():
        await fake_fab(registry=registry)
        for p in plugins:
            if hasattr(p, "fsql_connections"):
                p.fsql_provided = registry.resolve(list(p.fsql_connections))
                p.check_sql_connections()

    await init_hook()

    # SqlPlugin got its bundle.
    assert plugins[0].fsql_provided["report_database"] is fake_bundle
    assert plugins[0].f_init_error_log == ""

    # GhostSqlPlugin is missing its name.
    assert plugins[1].fsql_provided == {}
    assert "ghost_db" in plugins[1].f_init_error_log

    out = capsys.readouterr().out
    assert "ghost_db" in out


@pytest.mark.asyncio
async def test_startup_hook_survives_empty_registry(make_plugin_instance, capsys):
    """
    If fab registers nothing (e.g. primary DB unavailable), the hook
    must still complete and log per-plugin problems, not raise.
    """
    from space_station_stc.hull.plugin_abc.sql_registry import SQLConnectionRegistry

    registry = SQLConnectionRegistry()

    async def fake_fab(*, registry=None):
        return registry

    plugins = [make_plugin_instance( SqlPlugin )]

    async def init_hook():
        await fake_fab(registry=registry)
        for p in plugins:
            if hasattr(p, "fsql_connections"):
                p.fsql_provided = registry.resolve(list(p.fsql_connections))
                p.check_sql_connections()

    await init_hook()

    assert plugins[0].fsql_provided == {}
    assert "report_database" in plugins[0].f_init_error_log
    assert "report_database" in capsys.readouterr().out
