import datetime
from uuid import UUID
from typing import Annotated, Optional, List

from pydantic import BaseModel, SecretStr

# Page tree object
class ExternalDB_pdnt(BaseModel):
    id: Optional[UUID] = None
    resource_name: str
    connection_string : SecretStr
    expires_at : str
#