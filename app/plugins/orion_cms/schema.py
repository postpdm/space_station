import datetime
from uuid import UUID
from typing import Annotated, Optional, List

from pydantic import BaseModel

# Page tree object
class Page_Tree_Node_pdnt(BaseModel):
    id: Optional[UUID] = None
    title: str

# Main page object. Use it for light list of pages
class Page_pdnt(BaseModel):
    id: Optional[UUID] = None
    title: str

class Page_Section_pdnt(BaseModel):
    content : str
    content_type : int

class Page_Section_View_pdnt(BaseModel):
    id : UUID
    content : str
    content_type : int

class Page_Section_Create_pdnt(BaseModel):
    content : str

class Page_Section_Update_pdnt(BaseModel):
    content : str

# Main page with sections. Use it to get one page with all sub sections
class Page_with_sections_pdnt(BaseModel):
    id: Optional[UUID] = None
    title: str
    sections: List[Page_Section_View_pdnt] = []


class Tree_Node_Create_pdnt(BaseModel):
    title: str

class Tree_Node_Update_pdnt(BaseModel):
    title: str


class PageCreate_pdnt(BaseModel):
    title: str

class PageUpdate_pdnt(BaseModel):
    title: str

# Statistics
class Orion_Pages_Stat_Count_pdnt(BaseModel):
    total_page_count : int

class Orion_Pages_Stat_By_Day_pdnt(BaseModel):
    day : datetime.date
    count : int

class Orion_Manuscript_CodeRequest_pdnt(BaseModel):
    code : str

#