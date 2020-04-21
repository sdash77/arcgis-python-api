import os
import sys
import json
import uuid
from arcgis.gis import GIS
from arcgis import env as _env
from arcgis._impl.common._isd import InsensitiveDict

class KMLLayer(object):
    """
    The KMLLayer class is used to create a layer based on a KML file (.kml, .kmz).
    KML is an XML-based file format used to represent geographic features.

    ======================  =====================================================================
    **Arguement**           **Value**
    ----------------------  ---------------------------------------------------------------------
    url                     Required String.  The web location of the KML file.
    ----------------------  ---------------------------------------------------------------------
    gis                     Optional GIS. The connection object.
    ----------------------  ---------------------------------------------------------------------
    title                   Optional String. The title of the layer used to identify it in places such as the Legend and LayerList widgets.
    ----------------------  ---------------------------------------------------------------------
    id                      Optional String. The unique ID of the layer.
    ----------------------  ---------------------------------------------------------------------
    scale                   Optional Tuple. The min/max scale of the layer where the positions are: (min, max) as float values.
    ----------------------  ---------------------------------------------------------------------
    opacity                 Optional Float.  This value can range between 1 and 0, where 0 is 100 percent transparent and 1 is completely opaque.
    ======================  =====================================================================


    """
    _min_scale = None
    _max_scale = None
    _scale = None
    _type = "kml"
    def __init__(self, url, gis=None, **kwargs):
        """initializer"""
        self._url = url
        self._gis = gis or _env.active_gis or GIS()
        self._title = kwargs.pop('title', "KML Layer")
        self._min_scale, self._max_scale = kwargs.pop('scale', (-1,-1))
        self._opacity = kwargs.pop('opacity', 0)
        self._id = kwargs.pop('id', uuid.uuid4().hex)
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
    def scale(self) -> tuple:
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
    def _esri_json(self) -> dict:
        """creates a dictionary for web map item."""
        add_layer =  {
            "type" : "kml",
            'url' : self._url,
            'opacity' : self.opacity,
            'minScale' : self.scale[0],
            'maxScale' : self.scale[1],
            'id' : self._id,
            'title' : self.title
        }
        return add_layer