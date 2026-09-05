from pydantic import Field, HttpUrl, field_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Class for reading of environment file
class AppSettings(BaseSettings):
    # secret area
    inner_circle_key : SecretStr

    # Litestar specific native flags
    litestar_debug: bool = Field(default=True, validation_alias="LITESTAR_DEBUG")

    # App specific variables
    environment: str = "dev"
    #secret_key: str
    #allowed_hosts: list[str]
    #database_url: str

    # plugins
    plugin_packages: list[str] | None = None

    @field_validator("plugin_packages", mode="before")
    @classmethod
    def split_packages_string(cls, value: any) -> list[str]:
        """Convert str to list."""
        if isinstance(value, str):
            # .split() delete spaces
            return value.split()
        return value

    # Auth section
    AM_I_USER_URL : str | None = None
    AM_I_USER_LOGIN_FIELD : str | None = None
    AM_I_USER_NAME_FIELD : str | None = None
    AM_I_USER_SERVER_REQUEST : bool = True


    # GIS GeoServer settings
    GIS_USE_GEOSERVER : bool = False
    PROJECTION : str | None = None
    TILE_SIZE : int | None = None
    WMTS_ATTRIBUTIONS : str | None = None
    WMTS_URL : HttpUrl | None = None
    WMTS_LAYER : str | None = None
    WMS_URL : HttpUrl | None = None
    WMS_LAYERS : list[str] | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

#