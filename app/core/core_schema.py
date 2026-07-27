import datetime
from uuid import UUID
from typing import Annotated, Optional

from pydantic import BaseModel


# we will explicitly define the schema instead of using DTO objects for clarity.

class News_pdnt(BaseModel):
    id: Optional[UUID] = None
    title: str
    published_dt: Optional[datetime.datetime] = None


class NewsCreate_pdnt(BaseModel):
    title: str
    published_dt: Optional[datetime.datetime] = None

class NewsUpdate_pdnt(BaseModel):
    name: Optional[str] = None
    title: str
    published_dt: Optional[datetime.datetime] = None
