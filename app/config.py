from pathlib import Path
from litestar.plugins.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig

# Define the path to your templates directory
TEMPLATE_DIR = Path(__file__).parent / "templates"

# Configure the template engine
template_config = TemplateConfig(
    directory=TEMPLATE_DIR,
    engine=JinjaTemplateEngine,
)
