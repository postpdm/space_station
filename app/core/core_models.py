from advanced_alchemy.extensions.litestar import (
    base,
    #filters,
    #providers,
    #repository,
    #service,
)

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from typing import Annotated, Optional
import datetime


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