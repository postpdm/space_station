# GIS configuration

Space station support for external GIS map sources through OpenLayers visualisation library.

The connection originates from the client!

## Supported map sources

* Google Maps
* OpenStreetMap
* Internal GeoServer source


## Internal GeoServer

If you have an access to GeoServer, you can configure it in `.env` file.

See `.env.example`.

If GIS_USE_GEOSERVER = False then other options is skipped.