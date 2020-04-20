import json
import uuid
from arcgis.gis import GIS
from arcgis._impl.common._isd import InsensitiveDict
url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"

class GeoJSONLayer(object):
    """
    The GeoJSONLayer class is used to create a layer based on GeoJSON.
    GeoJSON is a format for encoding a variety of geographic data
    structures. The GeoJSON data must comply with the RFC 7946
    specification which states that the coordinates are in
    SpatialReference.WGS84.



    """
    #----------------------------------------------------------------------
    def __init__(self, url, gis=None, **kwargs):
        self._url = url
        self._type = "geojson"
        self._copyright = kwargs.pop("copyright", "")
        self._title = kwargs.pop("title", "GeoJSON Layer")
        self._id = kwargs.pop('id', uuid.uuid4().hex)
        self._minScale, self._maxScale = kwargs.pop('scale', (0,0))
        if 'renderer' in kwargs:
            r = kwargs.pop('renderer', None)
            if isinstance(r, dict):
                self._renderer = InsensitiveDict(r)
            else:
                self._renderer = None
        else:
            self._renderer = None
    #----------------------------------------------------------------------
    @property
    def title(self) -> str:
        """
        The title of the layer used to identify it in places such as the Legend and LayerList widgets.

        :returns: String
        """
        return self._title
    #----------------------------------------------------------------------
    @title.setter
    def title(self, value:str):
        """
        The title of the layer used to identify it in places such as the Legend and LayerList widgets.

        :returns: String
        """
        if self._title != value:
            self._title = value
    #----------------------------------------------------------------------
    @property
    def opacity(self) -> float:
        """
        This value can range between 1 and 0, where 0 is 100 percent transparent and 1 is completely opaque.

        :returns: Float
        """
        return self._opacity
    #----------------------------------------------------------------------
    @opacity.setter
    def opacity(self, value:float):
        """
        This value can range between 1 and 0, where 0 is 100 percent transparent and 1 is completely opaque.

        :returns: Float
        """
        if isinstance(value, (float, int)):
            self._opacity = value
    #----------------------------------------------------------------------
    @property
    def scale(self):
        """Gets/Sets the Min/Max Scale for the layer"""
        return self._min_scale, self._max_scale
    #----------------------------------------------------------------------
    @scale.setter
    def scale(self, scale:tuple):
        """Gets/Sets the Min/Max Scale for the layer"""
        if isinstance(scale, (tuple, list)) and len(scale) == 2:
            self._min_scale, self._max_scale = scale
    #----------------------------------------------------------------------
    @property
    def renderer(self):
        """Gets/Sets the renderer for the layer"""
        return self._renderer
    #----------------------------------------------------------------------
    @renderer.setter
    def renderer(self, renderer:dict):
        """Gets/Sets the renderer for the layer"""
        if isinstance(renderer, dict) and renderer:
            self._renderer = InsensitiveDict(renderer)
    #----------------------------------------------------------------------
    @property
    def _esri_json(self) -> dict:
        lyr = {
            "type" : self._type,
            "url" : self._url,
            "copyright" : self._copyright,
            "title" : self._title,
            "id" : self._id,
            "minScale" : self.scale[0],
            "maxScale" : self.scale[1]
        }
        if self._renderer:
            lyr['renderer'] = self._renderer._json
        return lyr
