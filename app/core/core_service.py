from advanced_alchemy.extensions.litestar import (
    repository,
    service,
)


from .core_models import GNN_Article_Model

class NewsService(service.SQLAlchemyAsyncRepositoryService[GNN_Article_Model]):
    """News repository."""

    class Repo(repository.SQLAlchemyAsyncRepository[GNN_Article_Model]):
        """News repository."""

        model_type = GNN_Article_Model

    repository_type = Repo


#