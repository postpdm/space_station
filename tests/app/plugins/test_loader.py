import pytest

from app.config import AppSettings
from app.plugins import get_all_ss_plugins

@pytest.mark.asyncio
async def test_package_settings():
    """Test package settings."""

    fake_env_data = {"plugin_packages": "some_package_name"}

    # Init config
    test_config = AppSettings(**fake_env_data)

    assert test_config.plugin_packages == ['some_package_name']

@pytest.mark.asyncio
async def test_loader():
    """Test plugin loader."""

    fake_env_data = {"plugin_packages": "ABRACADABRA_package"}

    # Init config
    test_config = AppSettings(**fake_env_data)

    assert test_config.plugin_packages == ['ABRACADABRA_package']

    # 5 standart plugins are exist
    assert len( get_all_ss_plugins( test_config ) ) == 5
