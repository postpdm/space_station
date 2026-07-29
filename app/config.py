from pathlib import Path
from litestar.plugins.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig
from litestar.static_files import StaticFilesConfig

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Define the path to your templates directory
TEMPLATE_DIR = Path(__file__).parent / "templates"

# Configure the template engine
template_config = TemplateConfig(
    directory=TEMPLATE_DIR,
    engine=JinjaTemplateEngine,
)


# Define the path to your static files directory
STATIC_DIR = Path(__file__).parent / "static"

# Configure the static files endpoint
static_config = StaticFilesConfig(
    path="/static",          # The URL prefix (e.g., http://localhost:8000/static/logo.png)
    directories=[STATIC_DIR], # List of directory paths to look up files
    html_mode=False,         # Set to True if serving a Single Page App (SPA) index.html
)


class AppSettings(BaseSettings):
    # Litestar specific native flags
    litestar_debug: bool = Field(default=True, validation_alias="LITESTAR_DEBUG")
    
    # App specific variables
    environment: str = "dev"
    #secret_key: str
    #allowed_hosts: list[str]
    #database_url: str
    
    # Auth section
    AM_I_USER_URL : str
    AM_I_USER_LOGIN_FIELD : str
    AM_I_USER_NAME_FIELD : str
    AM_I_USER_SERVER_REQUEST : bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache()
def get_settings() -> AppSettings:
    """Returns a cached settings instance to prevent repeated parsing."""
    return AppSettings()