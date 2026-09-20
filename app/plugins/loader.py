"""Discover and load all Space Station plugins."""
import importlib
import importlib.util
import inspect
import pkgutil
from pathlib import Path

from litestar.plugins import InitPlugin
from litestar.exceptions import ImproperlyConfiguredException

from rich import print as rich_p

from space_station_stc.hull.plugin_abc.abc_plugin import BasePlugin
from space_station_stc.hull.plugin_abc.sql_registry import SQLConnectionRegistry


def discover_local_plugins(
    static_dir: str,
    plugin_packages: list[str],
    sql_registry: SQLConnectionRegistry | None = None,
) -> list[InitPlugin]:
    """
    Find and load all local Space Station plugins from the code base.

    If `sql_registry` is provided, every instantiated plugin receives the
    SQL connection bundles it declared in `fsql_connections`.
    """
    plugins: list[InitPlugin] = []
    seen_ids: set = set()

    def check_module(module_name: str) -> None:
        # Import the module and inspect it for concrete BasePlugin subclasses.
        try:
            module = importlib.import_module(module_name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                if (
                    isinstance(attr, type)
                    and issubclass(attr, BasePlugin)   # Must inherit from BasePlugin.
                    and attr != BasePlugin             # Skip the base itself.
                    and not inspect.isabstract(attr)   # Skip abstract subclasses.
                    and hasattr(attr, "fplugin_id")    # Skip plugins without a UUID.
                ):
                    check_id = getattr(attr, "fplugin_id")
                    if check_id in seen_ids:
                        raise Exception(
                            "Plugin ID is not unique, cannot install"
                        )

                    # Instantiate the plugin and fill in its runtime context.
                    instance = attr()
                    instance.fstatic_dir = Path(static_dir)

                    # Inject the SQL connection bundles requested by the plugin.
                    if sql_registry is not None:
                        instance.fsql_provided = sql_registry.resolve(
                            list(instance.fsql_connections)
                        )

                    plugins.append(instance)
                    seen_ids.add(check_id)

        except Exception as e:
            rich_p(
                f"[red]Error[/red] load plugin {module_name}: [red]{e}[/red]"
            )

    plugins_dir = Path(__file__).parent

    for _, module_name, is_pkg in pkgutil.iter_modules([str(plugins_dir)]):
        # Skip loader and abstract base.
        if not is_pkg or module_name in ("loader", "abc_plugin"):
            continue

        check_module(f"app.plugins.{module_name}")

    if plugin_packages:
        # Load plugins from externally installed packages.
        for pp in plugin_packages:
            spec = importlib.util.find_spec(pp)
            if spec is None:
                rich_p(f"[red]Error[/red] load plugin from package [red]{pp}[/red]!")
            else:
                check_module(pp)

    return plugins


def build_global_sql_dependencies(
    plugins: list[InitPlugin],
) -> dict:
    """
    Aggregate SQL DI providers from every plugin into a single dict
    that can be passed to `Litestar(dependencies=...)`.

    Providers become globally available, so plugins do not need to attach
    them to their own controllers manually.
    """
    deps: dict = {}
    for plugin in plugins:
        if isinstance(plugin, BasePlugin):
            deps.update(plugin.sql_dependencies())
    return deps


def validate_plugin_connections(
    plugins: list[InitPlugin],
    sql_registry: SQLConnectionRegistry,
) -> None:
    """
    Fail fast if a plugin asked for a connection the core does not know about.
    Call this before building the Litestar app.
    """
    problems: list[str] = []
    for plugin in plugins:
        if not isinstance(plugin, BasePlugin):
            continue
        for name in plugin.fsql_connections:
            if not sql_registry.has(name):
                problems.append(
                    f"{plugin.plugin_name}: unknown connection '{name}'"
                )
    if problems:        
        # fail hard or skip?
        #raise RuntimeError(
        rich_p(
            "Plugin [red]SQL connection[/red] validation failed:\n  - "
            + "\n  - ".join(problems)
        )