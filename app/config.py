from pathlib import Path
from litestar.plugins.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig
from litestar.static_files import StaticFilesConfig

from functools import lru_cache

from .env_config import AppSettings

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
    name='static',
)

@lru_cache()
def get_settings() -> AppSettings:
    """Returns a cached settings instance to prevent repeated parsing."""
    return AppSettings()
    
#