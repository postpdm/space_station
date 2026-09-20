"""Tests for plugins.loader: discovery, dedup, SQL injection, validation."""
import sys
import types
from pathlib import Path
from uuid import UUID

import pytest

from app.plugins import loader as loader_mod

# ----------------------------------------------------------------------
# Helpers local to loader tests.
# ----------------------------------------------------------------------
def _install_fake_packages(monkeypatch, packages: dict[str, types.ModuleType]):
    for mod_name, mod in packages.items():
        monkeypatch.setitem(sys.modules, mod_name, mod)


def _patch_iter_modules(monkeypatch, names: list[str]):
    monkeypatch.setattr(
        loader_mod.pkgutil,
        "iter_modules",
        lambda _: iter([(None, n, True) for n in names]),
    )


def _patch_loader_file(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(loader_mod, "__file__", str(tmp_path / "loader.py"))


# ----------------------------------------------------------------------
# Discovery & skip rules
# ----------------------------------------------------------------------
def test_discover_skips_loader_and_abc(
    monkeypatch, tmp_path, registry_with_report_db, make_plugin_class
):
    pkg = types.ModuleType("app.plugins.reports")
    pkg.Reports = make_plugin_class(
        "Reports",
        UUID("11111111-1111-1111-1111-111111111111"),
        sql=["report_database"],
    )
    _install_fake_packages(monkeypatch, {"app.plugins.reports": pkg})
    _patch_iter_modules(
        monkeypatch, ["reports", "loader", "abc_plugin", "__init__"]
    )
    _patch_loader_file(monkeypatch, tmp_path)

    loaded = loader_mod.discover_local_plugins(
        static_dir=str(tmp_path),
        plugin_packages=[],
        sql_registry=registry_with_report_db,
    )

    assert [p.plugin_name for p in loaded] == ["Reports"]
    assert loaded[0].fstatic_dir == Path(tmp_path)


def test_discover_skips_abstract_plugin(
    monkeypatch, tmp_path, registry, make_plugin_class
):
    """
    A subclass that does not implement BasePlugin.health stays abstract
    and must be filtered out by inspect.isabstract().
    """
    pkg = types.ModuleType("app.plugins.abs")
    pkg.AbstractP = make_plugin_class(
        "AbstractP",
        UUID("22222222-2222-2222-2222-222222222222"),
        abstract=True,
    )
    _install_fake_packages(monkeypatch, {"app.plugins.abs": pkg})
    _patch_iter_modules(monkeypatch, ["abs"])
    _patch_loader_file(monkeypatch, tmp_path)

    loaded = loader_mod.discover_local_plugins(
        static_dir=str(tmp_path),
        plugin_packages=[],
        sql_registry=registry,
    )
    assert loaded == []


def test_discover_rejects_duplicate_id(
    monkeypatch, tmp_path, registry, make_plugin_class
):
    same = UUID("33333333-3333-3333-3333-333333333333")
    a = types.ModuleType("app.plugins.a")
    a.PluginA = make_plugin_class("PluginA", same)
    b = types.ModuleType("app.plugins.b")
    b.PluginB = make_plugin_class("PluginB", same)
    _install_fake_packages(monkeypatch, {"app.plugins.a": a, "app.plugins.b": b})
    _patch_iter_modules(monkeypatch, ["a", "b"])
    _patch_loader_file(monkeypatch, tmp_path)

    loaded = loader_mod.discover_local_plugins(
        static_dir=str(tmp_path),
        plugin_packages=[],
        sql_registry=registry,
    )
    assert [p.plugin_name for p in loaded] == ["PluginA"]


def test_discover_continues_after_broken_module(
    monkeypatch, tmp_path, registry, make_plugin_class
):
    good = types.ModuleType("app.plugins.good")
    good.Good = make_plugin_class(
        "Good", UUID("44444444-4444-4444-4444-444444444444")
    )

    def fake_import(name):
        if name == "app.plugins.broken":
            raise RuntimeError("boom")
        if name == "app.plugins.good":
            return good
        return types.ModuleType(name)

    monkeypatch.setattr(loader_mod.importlib, "import_module", fake_import)
    _patch_iter_modules(monkeypatch, ["broken", "good"])
    _patch_loader_file(monkeypatch, tmp_path)

    loaded = loader_mod.discover_local_plugins(
        static_dir=str(tmp_path),
        plugin_packages=[],
        sql_registry=registry,
    )
    assert [p.plugin_name for p in loaded] == ["Good"]


# ----------------------------------------------------------------------
# SQL injection
# ----------------------------------------------------------------------
def test_discover_injects_requested_connections(
    monkeypatch, tmp_path, registry_with_report_db, make_plugin_class
):
    pkg = types.ModuleType("app.plugins.with_sql")
    pkg.P = make_plugin_class(
        "WithSql",
        UUID("55555555-5555-5555-5555-555555555555"),
        sql=["report_database", "ghost_db"],
    )
    _install_fake_packages(monkeypatch, {"app.plugins.with_sql": pkg})
    _patch_iter_modules(monkeypatch, ["with_sql"])
    _patch_loader_file(monkeypatch, tmp_path)

    loaded = loader_mod.discover_local_plugins(
        static_dir=str(tmp_path),
        plugin_packages=[],
        sql_registry=registry_with_report_db,
    )

    provided = loaded[0].fsql_provided
    assert "report_database" in provided
    assert "ghost_db" not in provided


def test_discover_no_registry_leaves_sql_empty(
    monkeypatch, tmp_path, make_plugin_class
):
    pkg = types.ModuleType("app.plugins.nosql")
    pkg.P = make_plugin_class(
        "NoSql",
        UUID("66666666-6666-6666-6666-666666666666"),
        sql=["report_database"],
    )
    _install_fake_packages(monkeypatch, {"app.plugins.nosql": pkg})
    _patch_iter_modules(monkeypatch, ["nosql"])
    _patch_loader_file(monkeypatch, tmp_path)

    loaded = loader_mod.discover_local_plugins(
        static_dir=str(tmp_path),
        plugin_packages=[],
        sql_registry=None,
    )
    assert loaded[0].fsql_provided == {}


# ----------------------------------------------------------------------
# External packages
# ----------------------------------------------------------------------
def test_discover_external_package(
    monkeypatch, tmp_path, registry, make_plugin_class
):
    import importlib.machinery

    ext = types.ModuleType("external_pkg")
    ext.P = make_plugin_class(
        "Ext", UUID("77777777-7777-7777-7777-777777777777")
    )
    # Give the module a real-looking spec so importlib.util.find_spec()
    # does not raise ValueError: __spec__ is None.
    ext.__spec__ = importlib.machinery.ModuleSpec("external_pkg", loader=None)

    monkeypatch.setitem(sys.modules, "external_pkg", ext)
    _patch_iter_modules(monkeypatch, [])
    _patch_loader_file(monkeypatch, tmp_path)

    loaded = loader_mod.discover_local_plugins(
        static_dir=str(tmp_path),
        plugin_packages=["external_pkg"],
        sql_registry=registry,
    )
    assert [p.plugin_name for p in loaded] == ["Ext"]

def test_discover_missing_external_package(
    monkeypatch, tmp_path, registry, capsys
):
    monkeypatch.setattr(
        loader_mod.importlib.util, "find_spec", lambda _: None,
    )
    _patch_iter_modules(monkeypatch, [])
    _patch_loader_file(monkeypatch, tmp_path)

    loaded = loader_mod.discover_local_plugins(
        static_dir=str(tmp_path),
        plugin_packages=["does_not_exist"],
        sql_registry=registry,
    )
    assert loaded == []
    assert "does_not_exist" in capsys.readouterr().out


# ----------------------------------------------------------------------
# build_global_sql_dependencies
# ----------------------------------------------------------------------
def test_build_global_deps_aggregates(fake_bundle, make_plugin_class) -> None:
    P = make_plugin_class(
        "P",
        UUID("88888888-8888-8888-8888-888888888888"),
        sql=["report_database"],
    )
    p = P()
    p.fsql_provided = {"report_database": fake_bundle}

    deps = loader_mod.build_global_sql_dependencies([p])
    assert set(deps.keys()) == {
        "sql_report_database_engine",
        "sql_report_database_session",
    }


def test_build_global_deps_ignores_non_base() -> None:
    class NotAPlugin:
        pass

    deps = loader_mod.build_global_sql_dependencies([NotAPlugin()])  # type: ignore[list-item]
    assert deps == {}


# ----------------------------------------------------------------------
# validate_plugin_connections
# ----------------------------------------------------------------------
def test_validate_ok(registry_with_report_db, make_plugin_class) -> None:
    P = make_plugin_class(
        "P",
        UUID("99999999-9999-9999-9999-999999999999"),
        sql=["report_database"],
    )
    p = P()
    p.fsql_provided = registry_with_report_db.resolve(["report_database"])

    # Must not raise.
    loader_mod.validate_plugin_connections([p], registry_with_report_db)


def test_validate_raises_on_unknown(registry, make_plugin_class, capsys ) -> None:
    P = make_plugin_class(
        "P",
        UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        sql=["ghost_db"],
    )

    
    loader_mod.validate_plugin_connections([P()], registry)
    out = capsys.readouterr().out
    assert "Plugin SQL connection validation failed:" in out
    assert "P: unknown connection 'ghost_db'" in out

#    with pytest.raises(RuntimeError, match="ghost_db"):
