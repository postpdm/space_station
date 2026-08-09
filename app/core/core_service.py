from typing import Optional
from advanced_alchemy.extensions.litestar import (
    repository,
    service,
)
from sqlalchemy import select

from .core_models import User, UserFav, GNN_Article_Model

# AUTH

class UserRepository(repository.SQLAlchemyAsyncRepository[User]):
    model_type = User
    
    async def get_by_login(self, login: str) -> Optional[User]:
        query = select(User).where(User.user_login == login)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()    

class UserService(service.SQLAlchemyAsyncRepositoryService[User]):
    repository_type = UserRepository
    model_type = User

    async def get_or_create_user(self, user_login, user_name: str ) -> tuple[User, bool]:
        """
        Get or create user by login, Return User object and flag - False for get, True for create
        """
        existing_user = await self.repository.get_by_login( user_login )
        if existing_user:
            return existing_user, False  # get existing
            
        #new_user = await self.repository.create(user_in)
        new_user = User( user_login= user_login, user_name = user_name )
        self.repository.session.add( new_user )
        await self.repository.session.commit()  # commit
        return new_user, True  # return

# User fav

class UserFav_Service(service.SQLAlchemyAsyncRepositoryService[UserFav]):
    """User favorites repository."""

    class Repo(repository.SQLAlchemyAsyncRepository[UserFav]):
        """User favorites  repository."""

        model_type = UserFav

    repository_type = Repo

# NEWS

class NewsService(service.SQLAlchemyAsyncRepositoryService[GNN_Article_Model]):
    """News repository."""

    class Repo(repository.SQLAlchemyAsyncRepository[GNN_Article_Model]):
        """News repository."""

        model_type = GNN_Article_Model

    repository_type = Repo


#