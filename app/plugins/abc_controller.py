from abc import ABC, abstractmethod
from litestar import Controller, get
from litestar.response import Template

class BasePluginController(Controller, ABC):
    """
    Abstract controller for plugins.
    2 obligatory get's.
    """

#    @abstractmethod
#    @get("/home")
#    async def user_home_page(self) -> Template:
#        """User page."""

#    @abstractmethod
#    @get("/admin")
#    async def admin_panel(self) -> Template:
#        """Admin page."""
