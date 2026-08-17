import datetime
from uuid import UUID
from typing import Annotated, Optional, List

from pydantic import BaseModel

# Main page object. Use it for light list of pages
class Page_pdnt(BaseModel):
    id: Optional[UUID] = None
    title: str

class Page_Section_pdnt(BaseModel):
    content : str
    content_type : int

class Page_Section_Create_pdnt(BaseModel):
    content : str

# Main page with sections. Use it for one page with sub sections
class Page_with_sections_pdnt(BaseModel):
    id: Optional[UUID] = None
    title: str
    sections: List[Page_Section_pdnt] = []


class PageCreate_pdnt(BaseModel):
    title: str
    #content : str
    #published_dt: Optional[datetime.datetime] = None



#class NewsUpdate_pdnt(BaseModel):
#    title: str
#    content : str
#    published_dt: Optional[datetime.datetime] = None
