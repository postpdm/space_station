"""Tests for SQLConnectionRegistry."""
import pytest

from space_station_stc.hull.plugin_abc.sql_registry import SQLConnectionRegistry


def test_register_bundle_and_get(registry, fake_bundle) -> None:
    registry.register_bundle("a", fake_bundle)
    assert registry.has("a")
    assert registry.get("a") is fake_bundle


def test_register_engine_creates_sessionmaker(registry, fake_engine) -> None:
    registry.register_engine("a", fake_engine)
    bundle = registry.get("a")
    assert bundle.engine is fake_engine
    assert bundle.sessionmaker is not None


def test_register_engine_respects_session_kwargs(registry, fake_engine) -> None:
    registry.register_engine(
        "a", fake_engine, session_kwargs={"expire_on_commit": True}
    )
    bundle = registry.get("a")
    assert bundle.sessionmaker.kw.get("expire_on_commit") is True


def test_resolve_skips_missing(registry, fake_bundle) -> None:
    registry.register_bundle("a", fake_bundle)
    assert set(registry.resolve(["a", "b"]).keys()) == {"a"}


def test_resolve_empty_list_returns_empty(registry) -> None:
    assert registry.resolve([]) == {}


def test_all_names(registry, fake_bundle) -> None:
    registry.register_bundle("a", fake_bundle)
    registry.register_bundle("b", fake_bundle)
    assert set(registry.all_names()) == {"a", "b"}


def test_has_false_for_unknown(registry) -> None:
    assert not registry.has("nope")


def test_overwrite_same_name(registry, fake_bundle, fake_engine) -> None:
    registry.register_bundle("a", fake_bundle)
    registry.register_engine("a", fake_engine)
    assert registry.get("a").engine is fake_engine


@pytest.mark.asyncio
async def test_dispose_all_disposes_every_engine(registry, fake_engine) -> None:
    registry.register_engine("a", fake_engine)
    registry.register_engine("b", fake_engine)

    await registry.dispose_all()

    assert fake_engine.dispose.await_count == 2


@pytest.mark.asyncio
async def test_dispose_all_on_empty_registry_is_noop(registry) -> None:
    await registry.dispose_all()   # must not raise
