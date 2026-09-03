import pytest

from app.plugins import get_all_ss_plugins

@pytest.mark.asyncio
async def test_loader():
    """Test plugin loader."""
    # 5 standart plugins are exist
    assert len( get_all_ss_plugins() ) == 5
