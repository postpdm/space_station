import pytest
from anyio import Path
from app.plugins.orion_cms.parsers import CONST_PLAIN_MARKDOWN
from app.plugins.orion_cms.service_special import TextFileService, provide_file_service

# Turn anyio for pytest
pytestmark = pytest.mark.anyio

async def test_text_file_service_get_data(tmp_path):
    # anyio.Path
    test_dir = Path(tmp_path)
    file_path = test_dir / "test_page.md"
    
    # Write test data
    test_content = "# Hello World\nThis is a special CMS page."
    await file_path.write_text(test_content, encoding="utf-8")
    
    # Call service
    service = TextFileService()
    result = await service.get_data(file_path)
    
    
    # Check
    assert result["id"] == "special_help"
    assert result["title"] == "This is Help!"
    
    assert isinstance(result["sections"], list)
    assert result["sections"][0]["content"] == test_content
    assert result["sections"][0]["content_type"] == CONST_PLAIN_MARKDOWN

async def test_provide_file_service(tmp_path):
    # Test Litestar DI
    
    service = await provide_file_service()
    
    assert isinstance(service, TextFileService)
