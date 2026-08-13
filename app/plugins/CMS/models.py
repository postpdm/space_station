from advanced_alchemy.extensions.litestar import (
    base,
)

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from uuid import UUID
from typing import Annotated, Optional
import datetime

# CMS

class CMS_Article_Model(base.UUIDAuditBase):
    __tablename__ = "cms_article"
    title: Mapped[str]
    content: Mapped[str]
    
    created_user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    created_user: Mapped["User"] = relationship(lazy="joined", innerjoin=True, viewonly=True)

#