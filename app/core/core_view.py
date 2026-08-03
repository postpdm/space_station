from uuid import UUID
from dataclasses import dataclass
from typing import Annotated

import httpx

from litestar import Controller, Litestar, Request, delete, get, patch, post # we don't like "put"
from litestar.params import Dependency, PathParameter
from litestar.response import Template, Redirect

from litestar.params import URLEncodedBody

from advanced_alchemy.extensions.litestar import (
    filters,
    providers,
    service,
)

from .core_service import NewsService, UserService
from .core_models import User, GNN_Article_Model
from .core_schema import News_pdnt, NewsCreate_pdnt, NewsUpdate_pdnt, User_pdnt, UserCreate_pdnt, UserUpdate_pdnt

from ..config import AppSettings

# AUTH

@dataclass
class UserForm:
    user_login: str
    user_name: str


class UserController(Controller):
    path = "/users"

    dependencies = providers.create_service_dependencies(
        UserService,
        "user_service",
        load=[User],
        filters={"pagination_type": "limit_offset", "id_filter": UUID, "search": "user_name", "search_ignore_case": True},
    )

    async def set_session( self, request: Request, user_login : str, user_name : str ) -> None:
        print( 'set_session' )
        print( user_login )
        print( user_name )
        request.set_session( {"user_login": user_login, "user_name": user_name })

    @get("/login", exclude_from_auth=True) # exclude from auth require, elsewhere middleware redirect as infinitely
    async def login_page( self, app_settings: AppSettings, user_service: UserService, request: Request ) -> Template:
        try:
            if app_settings.AM_I_USER_URL:
                am_i_user_url = app_settings.AM_I_USER_URL
            else:
                am_i_user_url = 'http://127.0.0.1:8000/users/fake_user'

            if app_settings.AM_I_USER_LOGIN_FIELD:
                am_i_user_login_field = app_settings.AM_I_USER_LOGIN_FIELD
            else:
                am_i_user_login_field = 'userLogin'

            if app_settings.AM_I_USER_NAME_FIELD:
                am_i_user_name_field = app_settings.AM_I_USER_NAME_FIELD
            else:
                am_i_user_name_field = 'userName'

            server_request = app_settings.AM_I_USER_SERVER_REQUEST

            # is setting has a flag - TRY SERVER CONNECT
            if server_request:
                async with httpx.AsyncClient() as client:
                    response = await client.get( am_i_user_url )
                    # raise exception
                    response.raise_for_status()
                    js_data = response.json()
                    user_login = js_data.get( am_i_user_login_field )
                    user_name = js_data.get( am_i_user_name_field )
                    # we read login from server
                    await self.set_session( user_login, user_name )
                    
                    return Redirect(path='/')
                    
                    #return Template(
                    #    template_name = STAR_FORTRESS_TEMPLATES_DIR + "profile.html",
                    #    context={ 'server_request' : server_request, 'user_login' : user_login, 'user_name' : user_name, 'js_data' : js_data, 'error' : None }
                    #    )
            else:
                return Template(
                    template_name = "login.html",
                    context={ 'server_request' : server_request, 'am_i_user_url' : am_i_user_url, 'am_i_user_login_field' : am_i_user_login_field, 'am_i_user_name_field' : am_i_user_name_field }
                    )
        except:
            return Template(
                template_name = "login.html",
                context={ 'js_data' : None, 'error' : "can't fetch url " + am_i_user_url }
                )

            #return Template(template_name="login.html")


    @post("/login_form", exclude_from_auth=True) # exclude from auth require, elsewhere middleware redirect as infinitely
    async def login_form( self, request: Request, user_service: UserService, data: URLEncodedBody[UserForm] ) -> UserForm:
        
        print( 'login_form' )
        # check or create
        user, res = await user_service.get_or_create_user( data.user_login, data.user_name )
        
        print( user )
        print( res )
        if user:
            await self.set_session( request, user.user_login, user.user_name  )

        redirect_target = request.session.pop("next_url", "/")

        # check for evil Redirect attack
        if not redirect_target.startswith("/"):
            redirect_target = "/"
        return Redirect(path=redirect_target)

    @get('/fake_user', exclude_from_auth=True)
    async def get_fake_user(self) -> dict[str, str]:
        """Fake method for local testing purposes"""
        # Litestar automatically converts this dict to a JSON response
        return { "id": "123", "userLogin": "fake_domain\\fake_user", "userName": "Mr. Fake User jr.", 'some_key' : 'some_string' }


    @get(path="/list_users")
    async def list_users(
        self,
        user_service: UserService,
        filters: Annotated[list[filters.FilterTypes], Dependency(skip_validation=True)],
    ) -> service.OffsetPagination[User_pdnt]:
        """List users."""
        results, total = await user_service.get_many_and_count(*filters)
        return user_service.to_schema(results, total, filters=filters, schema_type=User_pdnt)

# News
class NewsController(Controller):
    """News CRUD"""

    dependencies = providers.create_service_dependencies(
        NewsService,
        "news_service",
        load=[GNN_Article_Model.sections],
        filters={"pagination_type": "limit_offset", "id_filter": UUID, "search": "title", "search_ignore_case": True},
    )

    @get(path="/news")
    async def list_news(
        self,
        news_service: NewsService,
        filters: Annotated[list[filters.FilterTypes], Dependency(skip_validation=True)],
    ) -> service.OffsetPagination[News_pdnt]:
        """List news."""
        results, total = await news_service.get_many_and_count(*filters)
        return news_service.to_schema(results, total, filters=filters, schema_type=News_pdnt)

    @post(path="/news")
    async def create_news(self, news_service: NewsService, data: NewsCreate_pdnt) -> News_pdnt:
        """Create a new news."""
        obj = await news_service.create(data)
        return news_service.to_schema(obj, schema_type=News_pdnt)

    # we override the news_repo to use the version that joins the Sections in
    @get(path="/news/{news_id:uuid}")
    async def get_news(
        self,
        news_service: NewsService,
        news_id: Annotated[
            UUID,
            PathParameter(
                title="News ID",
                description="The news to retrieve.",
            ),
        ],
    ) -> News_pdnt:
        """Get an existing news."""
        obj = await news_service.get(news_id)
        return news_service.to_schema(obj, schema_type=News_pdnt)

    @patch(path="/news/{news_id:uuid}")
    async def update_news(
        self,
        news_service: NewsService,
        data: NewsUpdate_pdnt,
        news_id: Annotated[
            UUID,
            PathParameter(
                title="News ID",
                description="The news to update.",
            ),
        ],
    ) -> News_pdnt:
        """Update an news."""
        obj = await news_service.update(data, item_id=news_id, auto_commit=True)
        return news_service.to_schema(obj, schema_type=News_pdnt)

    @delete(path="/news/{news_id:uuid}")
    async def delete_news(
        self,
        news_service: NewsService,
        news_id: Annotated[
            UUID,
            PathParameter(
                title="News ID",
                description="The news to delete.",
            ),
        ],
    ) -> None:
        """Delete a news from the system."""
        _ = await news_service.delete(news_id)

