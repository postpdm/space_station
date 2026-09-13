from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel

# External db connection object
class ExternalDB_pdnt(BaseModel):
    id: Optional[UUID] = None
    resource_name: str
    description: str
    connection_string : str
    expires_at : datetime

class ExternalDB_Check_pdnt(BaseModel):
    pass
    
#