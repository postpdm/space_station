'''
Service for special CMS pages.
'''

from typing import Protocol, Any, Optional

from anyio import Path

#class DataService(Protocol):
#    """Service."""
#    async def get_data(self) -> Any:
#        ...

class TextFileService:
    async def get_data(self) -> Any:
        p = "docs/cms/help.md"

        content = await Path(p).read_text(encoding="utf-8")
        print( content )

        return { "id" : '123-444',
                 "title": "This is Help!",
                 "sections": [ { "content" : content, "content_type" : 1911117 }
                             ] }

async def provide_file_service() -> TextFileService:
    # storage_dir=Path("./data_files")
    return TextFileService()
