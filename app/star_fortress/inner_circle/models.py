from enum import IntEnum

from datetime import datetime, timezone
from typing import Optional
from advanced_alchemy.base import UUIDAuditBase
from advanced_alchemy.types import EncryptedString
from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy import CheckConstraint, Integer, text

from space_station_stc.relic_transmission.validate_dt import SafeDateTime

from .context import db_encryption_key

class SourceType(IntEnum):
    SQL = 1
    FILE = 2
    API = 3

class ExternalDB(UUIDAuditBase):
    __tablename__ = "external_db"

    # some sources may be untested or expired
    active : Mapped[bool] = mapped_column( default=False )

    resource_name: Mapped[str] = mapped_column(unique=True)  # "analytics_postgres" or "ducklake"
    
    source_type: Mapped[int] = mapped_column(
        Integer,
        nullable=False,

        # default for SQLAlchemy
        default=SourceType.SQL.value,

        # default for server
        server_default=text("1"),
    )
    
    description: Mapped[str]

    # Advanced-Alchemy encrypted
    connection_safe_string: Mapped[str] # should not contain password! so we do not encrypt it
    connection_pw: Mapped[Optional[str]] = mapped_column(EncryptedString( default=None, key = lambda: db_encryption_key.get().get_secret_value() ) )

    # expire datetime
    expires_at: Mapped[Optional[datetime]] = mapped_column(SafeDateTime, index=True, nullable=True )

    @validates("source_type")
    def validate_source_type(
        self,
        key: str,
        value: int | SourceType,
    ) -> int:
        # bool is a subclass of int, so it must be rejected explicitly
        if isinstance(value, bool):
            raise ValueError(
                "source_type must be one of the following values: 1, 2, or 3"
            )

        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError(
                "source_type must be one of the following values: 1, 2, or 3"
            )

        allowed_values = {source_type.value for source_type in SourceType}

        if value not in allowed_values:
            raise ValueError(
                f"Invalid source type: {value}. "
                f"Allowed values: {sorted(allowed_values)}"
            )

        return value
        
    @validates('expires_at')
    def validate_expires_at(self, key, value):
        # Triggered when WRITING or UPDATING via SQLAlchemy
        # empry field is verbotten, SET NULL instead
        if isinstance(value, str) and value.strip() == '':
            return None
        else:
            return value

    # check expires
    @property
    def is_expired(self) -> bool:
        if self.expires_at:
            return datetime.now(timezone.utc) >= self.expires_at
        else:
            return False