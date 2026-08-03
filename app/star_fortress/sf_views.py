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

    @get('/profile')
    async def sf_profile(self, request: Request, app_settings: AppSettings ) -> Template:
        js_data = []
        user_name = None

        try:
            if app_settings.AM_I_USER_URL:
                am_i_user_url = app_settings.AM_I_USER_URL
            else:
                am_i_user_url = 'http://127.0.0.1:8000/star_fortress/fake_user'

            if app_settings.AM_I_USER_LOGIN_FIELD:
                am_i_user_login_field = app_settings.AM_I_USER_LOGIN_FIELD
            else:
                am_i_user_login_field = 'userLogin'

            if app_settings.AM_I_USER_NAME_FIELD:
                am_i_user_name_field = app_settings.AM_I_USER_NAME_FIELD
            else:
                am_i_user_name_field = 'userName'

            server_request = app_settings.AM_I_USER_SERVER_REQUEST

            if server_request:
                async with httpx.AsyncClient() as client:
                    response = await client.get( am_i_user_url )
                    # raise exception
                    response.raise_for_status()
                    js_data = response.json()
                    user_login = js_data.get( am_i_user_login_field )
                    user_name = js_data.get( am_i_user_name_field )

                    return Template(
                        template_name = STAR_FORTRESS_TEMPLATES_DIR + "profile.html",
                        context={ 'server_request' : server_request, 'user_login' : user_login, 'user_name' : user_name, 'js_data' : js_data, 'error' : None }
                        )
            else:
                return Template(
                    template_name = STAR_FORTRESS_TEMPLATES_DIR + "profile.html",
                    context={ 'server_request' : server_request, 'am_i_user_url' : am_i_user_url, 'am_i_user_login_field' : am_i_user_login_field, 'am_i_user_name_field' : am_i_user_name_field }
                    )
        except:
            return Template(
                template_name = STAR_FORTRESS_TEMPLATES_DIR + "profile.html",
                context={ 'js_data' : None, 'error' : "can't fetch url " + am_i_user_url }
                )


#