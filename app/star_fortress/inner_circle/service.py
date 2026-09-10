from typing import Optional
from advanced_alchemy.extensions.litestar import (
    repository,
    service,
)
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ExternalDB

class ExternalDBRepository(repository.SQLAlchemyAsyncRepository[ExternalDB]):
    model_type = ExternalDB

class ExternalDBService(service.SQLAlchemyAsyncRepositoryService[ExternalDB]):
    repository_type = ExternalDBRepository
    model_type = ExternalDB
