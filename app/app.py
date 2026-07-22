from litestar import Litestar, get


@get("/")
async def index() -> str:
    """Handler function that returns a greeting dictionary."""
    return "Space station"


app = Litestar(route_handlers=[index])