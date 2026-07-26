from litestar import Litestar

from .config import template_config
from .user_portal.up_views import User_Portal_Controller
from .star_fortress.sf_views import Star_Fortress_Controller

app = Litestar( route_handlers=[User_Portal_Controller, Star_Fortress_Controller],
    template_config=template_config,
)
