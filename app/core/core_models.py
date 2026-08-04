from advanced_alchemy.extensions.litestar import (
    base,
)

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
#from advanced_alchemy.extensions.litestar.session import SessionModelMixin

from uuid import UUID
from typing import Annotated, Optional
import datetime

# AUTH section

class User(base.UUIDBase):
    user_login: Mapped[str] = mapped_column( unique=True) # unique
    user_name: Mapped[str]  # not unique

## AUTH sessions in db
# Session model
#class WebSession(SessionModelMixin):
#    __tablename__ = "web_sessions"


# GNN — Galactic News Network

class GNN_Article_Model(base.UUIDAuditBase):
    __tablename__ = "gnn_article"
    title: Mapped[str]
    content: Mapped[str]
    published_dt: Mapped[Optional[datetime.datetime]]

    created_user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    created_user: Mapped["User"] = relationship(lazy="joined", innerjoin=True, viewonly=True)

#