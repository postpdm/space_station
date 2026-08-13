from typing import Optional
from advanced_alchemy.extensions.litestar import (
    repository,
    service,
)
from sqlalchemy import select

from .models import CMS_Article_Model

# CMS

class CMSRepository(repository.SQLAlchemyAsyncRepository[CMS_Article_Model]):
    model_type = CMS_Article_Model
    

class CMSService(service.SQLAlchemyAsyncRepositoryService[CMS_Article_Model]):
    repository_type = CMSRepository
    model_type = CMS_Article_Model

#