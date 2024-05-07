from functools import lru_cache
from arcgis.auth.tools import LazyLoader

_arcgis = LazyLoader("arcgis")


class BasemapService:
    """
    The basemap styles service is a ready-to-use location service that serves vector
    and image tiles that represent geographic features around the world. It includes
    styles that represent topographic features, road networks, footpaths, building
    footprints, water features, administrative boundaries, and satellite imagery.
    The styles are returned as JSON based on the Mapbox Style Specification or the ArcGIS
    Web Map Specification. The service also supports displaying localized language place
    labels, places, and worldviews. Custom basemap styles can also be created from the the default styles.

    When you are using a rendered Map instance, you can specify the basemap service to the basemap
    property to apply the style to the map.
    """

    def __init__(self, gis=None) -> None:
        self._gis = gis if gis else _arcgis.env.active_gis
        self._session = self._gis._session
        self._construct_styles_name_to_path

    @property
    def _construct_styles_name_to_path(self):
        """
        Constructs a dictionary of basemap style names to their respective paths.
        """
        url = "https://basemapstyles-api.arcgis.com/arcgis/rest/services/styles/v2/styles/self"
        params = {"f": "json"}
        resp = self._session.get(url, params=params)
        styles_dict = resp.json()["styles"]

        style_names = [style["name"] for style in styles_dict]
        paths = [style["path"] for style in styles_dict]
        self._styles_name_to_path = dict(zip(style_names, paths))

    def styles(self) -> list[str]:
        """
        Returns a list of available basemap styles and their respective path.
        """
        return self._styles_name_to_path

    def get_style(
        self, style_name: str | None = None, style_path: str | None = None
    ) -> dict:
        """
        Returns the style JSON for the specified style name or path.
        """
        if style_name and style_name not in self._styles_name_to_path:
            raise ValueError(f"Style '{style_name}' is not available.")
        elif style_path and style_path not in self._styles_name_to_path.values():
            raise ValueError(f"Style path '{style_path}' is not available.")

        path = style_path if style_path else self._styles_name_to_path[style_name]
        url = f"https://basemapstyles-api.arcgis.com/arcgis/rest/services/styles/v2/styles/{path}"
        params = {"f": "json"}
        resp = self._session.get(url, params=params)
        return resp.json()

    @property
    def languages(self):
        """
        Returns a list of supported languages for the basemap styles.
        """
        url = "https://basemapstyles-api.arcgis.com/arcgis/rest/services/styles/v2/styles/self"
        params = {"f": "json"}
        resp = self._session.get(url, params=params)
        return resp.json()["languages"]

    @property
    def places(self):
        """
        Returns a list of supported places for the basemap styles.
        """
        url = "https://basemapstyles-api.arcgis.com/arcgis/rest/services/styles/v2/styles/self"
        params = {"f": "json"}
        resp = self._session.get(url, params=params)
        return resp.json()["places"]
