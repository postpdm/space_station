'''
Service for special CMS pages.
'''

from typing import Protocol, Any, Optional

#class DataService(Protocol):
#    """Service."""
#    async def get_data(self) -> Any:
#        ...

class TextFileService:
    async def get_data(self) -> Any:
        return { "id" : '123-444', 
                    "title": "This is Help!",
                    "sections": [ { "content" : "### Here is a great section", "content_type" : 1911117 },
                                  {"content" : "\n| Left Aligned | Center Aligned | Right Aligned |\n| :---         |     :---:      |          ---: |\n| Text         | More Text      | $100          |\n\n","content_type":1911117 } ] }

async def provide_file_service() -> TextFileService:
    # storage_dir=Path("./data_files")
    return TextFileService()
