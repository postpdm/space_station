'''
Service for special CMS pages.
'''

from typing import Any

from anyio import Path

from .parsers import CONST_PLAIN_MARKDOWN

class TextFileService:
    async def get_data(self, p) -> Any:
        content = await Path(p).read_text(encoding="utf-8")

        return { "id" : 'special_help',
                 "title": "This is Help!",
                 "sections": [ { "content" : content, "content_type" : CONST_PLAIN_MARKDOWN }
                             ] }

async def provide_file_service() -> TextFileService:
    return TextFileService()
