import datetime
from uuid import UUID
from typing import Annotated, Optional

from pydantic import BaseModel

class Page_pdnt(BaseModel):
    id: Optional[UUID] = None
    title: str
    content : str
    published_dt: Optional[datetime.datetime] = None
    created_user_id : UUID
    #created_user : User_pdnt

class NewPageCreate_pdnt(BaseModel):
    title: str
    content : str
    #published_dt: Optional[datetime.datetime] = None

#class NewsUpdate_pdnt(BaseModel):
#    title: str
#    content : str
#    published_dt: Optional[datetime.datetime] = None
