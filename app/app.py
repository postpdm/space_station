from litestar import Litestar

from .config import template_config
from .user_portal.views import User_Portal_Controller

app = Litestar( route_handlers=[User_Portal_Controller],
    template_config=template_config,
)