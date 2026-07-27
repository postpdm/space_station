from uuid import UUID
from typing import Annotated, Optional

from litestar import Controller, Litestar, delete, get, patch, post
from litestar.params import Dependency, PathParameter

from advanced_alchemy.extensions.litestar import (
    filters,
    providers,
    service,
)

from .core_service import NewsService
from .core_models import GNN_Article_Model
from .core_schema import News_pdnt, NewsCreate_pdnt, NewsUpdate_pdnt

class NewsController(Controller):
    """News CRUD"""

    dependencies = providers.create_service_dependencies(
        NewsService,
        "news_service",
        load=[GNN_Article_Model.sections],
        filters={"pagination_type": "limit_offset", "id_filter": UUID, "search": "title", "search_ignore_case": True},
    )

    @get(path="/news")
    async def list_news(
        self,
        news_service: NewsService,
        filters: Annotated[list[filters.FilterTypes], Dependency(skip_validation=True)],
    ) -> service.OffsetPagination[News_pdnt]:
        """List news."""
        results, total = await news_service.get_many_and_count(*filters)
        return news_service.to_schema(results, total, filters=filters, schema_type=News_pdnt)

    @post(path="/news")
    async def create_news(self, news_service: NewsService, data: NewsCreate_pdnt) -> News_pdnt:
        """Create a new news."""
        obj = await news_service.create(data)
        return news_service.to_schema(obj, schema_type=News_pdnt)

    # we override the news_repo to use the version that joins the Sections in
    @get(path="/news/{news_id:uuid}")
    async def get_news(
        self,
        news_service: NewsService,
        news_id: Annotated[
            UUID,
            PathParameter(
                title="News ID",
                description="The news to retrieve.",
            ),
        ],
    ) -> News_pdnt:
        """Get an existing news."""
        obj = await news_service.get(news_id)
        return news_service.to_schema(obj, schema_type=News_pdnt)

    @patch(path="/news/{news_id:uuid}")
    async def update_news(
        self,
        news_service: NewsService,
        data: NewsUpdate_pdnt,
        news_id: Annotated[
            UUID,
            PathParameter(
                title="News ID",
                description="The news to update.",
            ),
        ],
    ) -> News_pdnt:
        """Update an news."""
        obj = await news_service.update(data, item_id=news_id, auto_commit=True)
        return news_service.to_schema(obj, schema_type=News_pdnt)

    @delete(path="/news/{news_id:uuid}")
    async def delete_news(
        self,
        news_service: NewsService,
        news_id: Annotated[
            UUID,
            PathParameter(
                title="News ID",
                description="The news to delete.",
            ),
        ],
    ) -> None:
        """Delete a news from the system."""
        _ = await news_service.delete(news_id)

