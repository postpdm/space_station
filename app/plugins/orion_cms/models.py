from advanced_alchemy.extensions.litestar import (
    base,
)

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from uuid import UUID
from typing import Annotated, Optional, List
import datetime

# CMS

# page it's just a title
class CMS_Page_Model(base.UUIDAuditBase):
    __tablename__ = "cms_page"
    title: Mapped[str]

    sections: Mapped[List["CMS_Page_Section_Model"]] = relationship(
        back_populates="page", 
        cascade="all, delete-orphan",
        lazy="selectin"  # auto load
    )

class CMS_Page_Section_Model(base.UUIDAuditBase):
    __tablename__ = "cms_page_section"

    content: Mapped[str]
    content_type: Mapped[int]
   
    page_id: Mapped[UUID] = mapped_column(ForeignKey("cms_page.id"))
    page: Mapped[CMS_Page_Model] = relationship( back_populates="sections", lazy="joined", innerjoin=True, viewonly=True)
    
#
