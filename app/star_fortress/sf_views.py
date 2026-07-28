from litestar import Controller, Request, get
from litestar.response import Template

import httpx

from ..config import AppSettings

STAR_FORTRESS_TEMPLATES_DIR = "star_fortress/"

class Star_Fortress_Controller(Controller):
    path = "/star_fortress"

    @get('/')
    async def sf_index_handler(self, request: Request) -> Template:

        # Access to app through request
        app_instance = request.app
        cached_plugins = request.app.state.active_plugins

        # Get all plugins
        plugin_names = [
            type(plugin).__name__ for plugin in app_instance.plugins.init
        ]

        return Template(
            template_name = STAR_FORTRESS_TEMPLATES_DIR + "index.html",
            context={ 'installed_plugin_names' : plugin_names, 'cached_plugins' : cached_plugins }
        )

    @get('/fake_user')
    async def get_fake_user(self) -> dict[str, str]:
        """Fake method for local testing purposes"""
        # Litestar automatically converts this dict to a JSON response
        return { "id": "123", "userName": "fake_user", 'some_key' : 'some_string' }

    @get('/profile')
    async def sf_profile(self, request: Request, app_settings: AppSettings ) -> Template:
        js_data = []

        try:
            if app_settings.AM_I_USER_URL:
                am_i_user_url = app_settings.AM_I_USER_URL
            else:
                am_i_user_url = 'http://127.0.0.1:8000/star_fortress/fake_user'
            
            if app_settings.AM_I_USER_FIELD:
                am_i_user_field = app_settings.AM_I_USER_FIELD
            else:
                am_i_user_field = 'userName'

            async with httpx.AsyncClient() as client:
                response = await client.get( am_i_user_url )
                # Выбрасывает исключение для плохих HTTP-статусов (опционально)
                response.raise_for_status()
                js_data = response.json()
                user_name = js_data.get( am_i_user_field )

            return Template(
                template_name = STAR_FORTRESS_TEMPLATES_DIR + "profile.html",
                context={ 'user_name' : user_name, 's' : js_data, 'error' : None }
            )
        except:
            return Template(
                template_name = STAR_FORTRESS_TEMPLATES_DIR + "profile.html",
                context={ 'user_name' : user_name, 's' : None, 'error' : "can't fetch url " + am_i_user_url }
                )


#