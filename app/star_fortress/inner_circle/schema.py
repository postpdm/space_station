from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, field_validator

# External db connection object
class ExternalDB_pdnt(BaseModel):
    id: Optional[UUID] = None
    resource_name: str
    description: str
    connection_safe_string : str
    connection_pw : Optional[str]
    expires_at : Optional[datetime] = None

    @field_validator("expires_at", mode="before")
    @classmethod
    def empty_to_none(cls, v):
        if v in ("", "null", "None", None):
            return None
        return v

class ExternalDB_Check_pdnt(BaseModel):
    pass
    
#