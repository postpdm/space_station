from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

# Class for reading of environment file
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
    
    
    # GIS GeoServer settings
    GIS_USE_GEOSERVER : bool = False
    PROJECTION : str
    TILE_SIZE : int
    WMTS_ATTRIBUTIONS : str
    WMTS_URL : HttpUrl
    WMTS_LAYER : str
    WMS_URL : HttpUrl
    WMS_LAYERS : list[str]
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

#