"""Tests for app.plugins.__init__.get_all_ss_plugins."""
from unittest.mock import MagicMock

from app import plugins as plugins_pkg
from app.plugins import get_all_ss_plugins


def test_get_all_passes_static_dir_and_packages(monkeypatch):
    captured = {}

    def fake_discover(static_dir, plugin_packages, sql_registry=None):
        captured.update(
            static_dir=static_dir,
            plugin_packages=plugin_packages,
            sql_registry=sql_registry,
        )
        return []

    # Patch on the package module, because get_all_ss_plugins imported
    # discover_local_plugins into its own namespace.
    monkeypatch.setattr(
        plugins_pkg, "discover_local_plugins", fake_discover, raising=False
    )

    settings = MagicMock()
    settings.plugin_packages = ["pkg_a", "pkg_b"]
    reg = MagicMock()

    result = get_all_ss_plugins(settings, reg)

    assert captured["plugin_packages"] == ["pkg_a", "pkg_b"]
    assert captured["sql_registry"] is reg
    assert result == []


def test_get_all_passes_registry(monkeypatch):
    captured = {}

    def fake_discover(static_dir, plugin_packages, sql_registry=None):
        captured["registry"] = sql_registry
        return []

    monkeypatch.setattr(
        plugins_pkg, "discover_local_plugins", fake_discover, raising=False
    )

    settings = MagicMock(plugin_packages=[])
    reg = MagicMock()
    get_all_ss_plugins(settings, reg)

    assert captured["registry"] is reg