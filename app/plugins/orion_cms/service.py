from typing import Optional
from advanced_alchemy.extensions.litestar import (
    repository,
    service,
)
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

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

class CMS_ReportService:
    """CMS complex analytics"""
    def __init__(self, db_session: AsyncSession) -> None:
        self.session = db_session

    async def get_page_count(self) -> int:
        query = select(func.count()).select_from(CMS_Page_Model)
        result = await self.session.scalar(query)
        return result
    
    async def get_page_by_day_count(self) -> int:
        date_col = func.date(CMS_Page_Model.created_at).label("day")
        stmt = (
            select(date_col, func.count(CMS_Page_Model.id).label("count"))
            .group_by(date_col)
            .order_by(date_col.desc())
        )
        
        result = await self.session.execute(stmt)
        return [{"day": row.day, "count": row.count} for row in result.all()]
        

async def provide_cms_report_service(db_session: AsyncSession) -> CMS_ReportService:
    return CMS_ReportService(db_session=db_session)


#