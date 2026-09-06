import pytest

from app.config import AppSettings

@pytest.mark.asyncio
async def test_CDN_false() -> None:
    fake_env_data = { "USE_CDN" : False }

    # Init config
    test_config = AppSettings(**fake_env_data)

    assert test_config.USE_CDN == False


@pytest.mark.asyncio
async def test_CDN_true() -> None:

    fake_env_data = { "USE_CDN" : True }

    # Init config
    test_config = AppSettings(**fake_env_data)

    assert test_config.USE_CDN == True
