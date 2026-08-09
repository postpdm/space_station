import datetime
from uuid import UUID
from typing import Annotated, Optional

from pydantic import BaseModel

class User_pdnt(BaseModel):
    user_login : str
    user_name : str

class UserCreate_pdnt(BaseModel):
    user_login : str
    user_name : str

class UserUpdate_pdnt(BaseModel):
    user_login : str
    user_name : str

# User fav

class UserFav_pdnt(BaseModel):
    whose_user_fav_id : UUID
    whose_user_fav : User_pdnt
    plugin_UUID : UUID

class UserFavCreate_pdnt(BaseModel):
    plugin_UUID : UUID

# we will explicitly define the schema instead of using DTO objects for clarity.

class News_pdnt(BaseModel):
    id: Optional[UUID] = None
    title: str
    content : str
    published_dt: Optional[datetime.datetime] = None
    created_user_id : UUID
    created_user : User_pdnt

class NewsCreate_pdnt(BaseModel):
    title: str
    content : str
    published_dt: Optional[datetime.datetime] = None

class NewsUpdate_pdnt(BaseModel):
    title: str
    content : str
    published_dt: Optional[datetime.datetime] = None
