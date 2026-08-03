from litestar import get
from litestar.status_codes import HTTP_204_NO_CONTENT

# shut it up
@get("/favicon.ico", exclude_from_auth=True, status_code=HTTP_204_NO_CONTENT)
async def favicon( ) -> None:
    return None
