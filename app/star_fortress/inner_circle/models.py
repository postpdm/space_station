from datetime import datetime, timezone
from typing import Optional
from advanced_alchemy.base import UUIDAuditBase
from advanced_alchemy.types import EncryptedString
from sqlalchemy.orm import Mapped, mapped_column

from .context import db_encryption_key

class ExternalCredential(UUIDAuditBase):
    __tablename__ = "external_credential"

    resource_name: Mapped[str] = mapped_column(unique=True)  # "analytics_postgres" or "ducklake"
    
    # Advanced-Alchemy encrypted
    api_key_or_connection_string: Mapped[str] = mapped_column(EncryptedString( key = lambda: db_encryption_key.get() ) )
    
    # expire datetime
    expires_at: Mapped[datetime] = mapped_column(index=True)

    # check expires
    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at
