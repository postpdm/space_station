from typing import Optional
from advanced_alchemy.extensions.litestar import (
    repository,
    service,
)
from sqlalchemy import select

from .models import CMS_Page_Model, CMS_Page_Section_Model

# CMS

class CMSRepository(repository.SQLAlchemyAsyncRepository[CMS_Page_Model]):
    model_type = CMS_Page_Model


class CMSService(service.SQLAlchemyAsyncRepositoryService[CMS_Page_Model]):
    repository_type = CMSRepository
    model_type = CMS_Page_Model

class CMS_Section_Repository(repository.SQLAlchemyAsyncRepository[CMS_Page_Section_Model]):
    model_type = CMS_Page_Section_Model

class CMS_Section_Service(service.SQLAlchemyAsyncRepositoryService[CMS_Page_Section_Model]):
    repository_type = CMS_Section_Repository
    model_type = CMS_Page_Section_Model

#
