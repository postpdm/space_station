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

# The `AuditBase` class includes the same UUID` based primary key (`id`) and 2
# additional columns: `created` and `updated`. `created` is a timestamp of when the
# record created, and `updated` is the last time the record was modified.
# the SQLAlchemy base includes a declarative model for you to use in your models.
# The `Base` class includes a `UUID` based primary key (`id`)

class GNN_Article_Section_Model(base.UUIDBase):
    # we can optionally provide the table name instead of auto-generating it
    __tablename__ = "gnn_article_section"
    content: Mapped[str]
    gnn_article_id: Mapped[UUID] = mapped_column(ForeignKey("gnn_article.id"))
    gnn_article: Mapped["GNN_Article_Model"] = relationship(lazy="joined", innerjoin=True, viewonly=True)

class GNN_Article_Model(base.UUIDAuditBase):
    __tablename__ = "gnn_article"
    title: Mapped[str]
    published_dt: Mapped[Optional[datetime.datetime]]
    sections: Mapped[list[GNN_Article_Section_Model]] = relationship(back_populates="gnn_article", lazy="selectin")

#