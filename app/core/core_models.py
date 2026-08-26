from advanced_alchemy.extensions.litestar import (
    base,
)

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
#from advanced_alchemy.extensions.litestar.session import SessionModelMixin

from uuid import UUID, uuid4
from typing import Annotated, Optional
import datetime

# AUTH section

class User(base.UUIDBase):
    user_login: Mapped[str] = mapped_column( unique=True) # unique
    user_name: Mapped[str]  # not unique
    is_mechanoid : Mapped[bool] = mapped_column( default=False )
    pseudo_name: Mapped[str] = mapped_column( default=str( uuid4() ) ) # not unique

# User fav
class UserFav(base.UUIDBase):
    # Define the multi-column unique constraint here
    __table_args__ = (
        UniqueConstraint("whose_user_fav_id", "plugin_UUID", name="uq_user_fav_plugin"),
    )
    
    whose_user_fav_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    whose_user_fav: Mapped["User"] = relationship(lazy="joined", innerjoin=True, viewonly=True)
    plugin_UUID : Mapped[UUID]


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