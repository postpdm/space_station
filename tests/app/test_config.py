import pytest

import secrets

from app.config import AppSettings

@pytest.mark.asyncio
async def test_CDN_false() -> None:
    hex_key = secrets.token_hex(16)

    fake_env_data = { "inner_circle_key" : hex_key, "USE_CDN" : False }

    # Init config
    test_config = AppSettings(**fake_env_data)

    assert test_config.USE_CDN == False


@pytest.mark.asyncio
async def test_CDN_true() -> None:
    hex_key = secrets.token_hex(16)
    
    fake_env_data = { "inner_circle_key" : hex_key, "USE_CDN" : True }

    # Init config
    test_config = AppSettings(**fake_env_data)

    assert test_config.USE_CDN == True
