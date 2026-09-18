from datetime import datetime, timezone
from typing import Optional
from advanced_alchemy.base import UUIDAuditBase
from advanced_alchemy.types import EncryptedString
from sqlalchemy.orm import Mapped, mapped_column

from .context import db_encryption_key

class ExternalDB(UUIDAuditBase):
    __tablename__ = "external_db"

    resource_name: Mapped[str] = mapped_column(unique=True)  # "analytics_postgres" or "ducklake"
    
    description: Mapped[str]
    
    # Advanced-Alchemy encrypted
    connection_safe_string: Mapped[str] # should not contain password! so we do not encrypt it
    connection_pw: Mapped[Optional[str]] = mapped_column(EncryptedString( default=None, key = lambda: db_encryption_key.get().get_secret_value() ) )
    
    # expire datetime
    expires_at: Mapped[Optional[datetime]] = mapped_column(index=True)

    # check expires
    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at
