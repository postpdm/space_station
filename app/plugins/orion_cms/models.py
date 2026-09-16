from advanced_alchemy.extensions.litestar import (
    base,
)

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from uuid import UUID
from typing import Annotated, Optional, List
import datetime

# CMS

# Page tree
class CMS_Tree_Model(base.UUIDAuditBase):
    __tablename__ = "cms_tree"
    title: Mapped[str]
    
    pages: Mapped[List["CMS_Page_Model"]] = relationship(
        back_populates="tree", 
        cascade="all, delete-orphan",
        lazy="selectin"  # auto load
    )

# page itself is just a title
class CMS_Page_Model(base.UUIDAuditBase):
    __tablename__ = "cms_page"
    title: Mapped[str]

    tree_id: Mapped[UUID] = mapped_column(ForeignKey("cms_tree.id"))
    tree: Mapped[CMS_Tree_Model] = relationship( back_populates="pages", lazy="joined", innerjoin=True, viewonly=True)

    sections: Mapped[List["CMS_Page_Section_Model"]] = relationship(
        back_populates="page", 
        cascade="all, delete-orphan",
        lazy="selectin"  # auto load
    )

class CMS_Page_Section_Model(base.UUIDAuditBase):
    __tablename__ = "cms_page_section"

    content: Mapped[str]
    content_type: Mapped[int]
    position : Mapped[int] = mapped_column( default=0 )
   
    page_id: Mapped[UUID] = mapped_column(ForeignKey("cms_page.id"))
    page: Mapped[CMS_Page_Model] = relationship( back_populates="sections", lazy="joined", innerjoin=True, viewonly=True)
    
#
