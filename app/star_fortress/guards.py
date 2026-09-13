from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException, PermissionDeniedException
from litestar.handlers import BaseRouteHandler

# Admins only
def admin_guard(connection: ASGIConnection, handler: BaseRouteHandler) -> None:

    arch_tech_priest = connection.session.get("arch_tech_priest")

    if not arch_tech_priest:
        raise PermissionDeniedException(detail="Only ARCH TECH-PRIESTS shall pass! Unsanctioned flesh will be scoured." )
