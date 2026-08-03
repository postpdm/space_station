from litestar.connection import ASGIConnection
from litestar.middleware.base import DefineMiddleware
from litestar import Request, get, post
from litestar.response import Redirect, Template

from litestar.middleware import (
   AbstractAuthenticationMiddleware,
   AuthenticationResult,
)

#from .core_service import UserRepository
#from .core_models import User

from litestar.exceptions.http_exceptions import NotAuthorizedException

class CustomAuthenticationMiddleware(AbstractAuthenticationMiddleware):
    async def authenticate_request(self, connection: ASGIConnection) -> AuthenticationResult:
        """Given a request, parse the request api key stored in the header and retrieve the user correlating to the token from the DB"""

        # retrieve the auth header
        auth_header = connection.session.get("user_login")
        if not auth_header:
            raise NotAuthorizedException()

        # check user

        #if user:
        #    pass
        #else:
        #    raise NotAuthorizedException()
        #if not user.user_login:
        #    raise NotAuthorizedException()
        return AuthenticationResult( user= auth_header, auth=True )

# Exception Handler
# For case then middleware raise NotAuthorizedException, redirect to login page
def auth_exception_handler(request: Request, exception: Exception) -> Redirect:
    next_url = request.url.path
    #request.session["next_url"] = request.url.path
    request.set_session( { "next_url" : request.url.path } )
            
    return Redirect(path= "/users/login")

# you can optionally exclude certain paths from authentication.
# the following excludes all routes mounted at or under `/schema*`
auth_mw = DefineMiddleware(CustomAuthenticationMiddleware, exclude="schema")
