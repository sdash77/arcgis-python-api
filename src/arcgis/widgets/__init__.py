"""
The arcgis.widgets module provides components for visualizing GIS data and analysis.
This module includes the MapView Jupyter notebook widget for visualizing maps and layers
"""
import json
import random
import string

from arcgis.features import FeatureSet
from arcgis.gis import Layer
from arcgis.mapping import WebMap


try:
    from ipywidgets import widgets
except:
    from IPython.html import widgets

try:
    from traitlets import Unicode, Int, List, Bool
except:
    from IPython.utils.traitlets import Unicode, Int, List, Bool


class MapView(widgets.DOMWidget):
    """Mapping widget for Jupyter Notebook"""
    _view_name = Unicode('MapView').tag(sync=True)
    _view_module = Unicode('mapview').tag(sync=True)

    # value = Unicode('Hello World!').tag(sync=True)

    basemap = Unicode('topo').tag(sync=True)
    width = Unicode('100%').tag(sync=True)
    zoom = Int(2).tag(sync=True)
    id = Unicode('').tag(sync=True)
    center = List([0, 0]).tag(sync=True)
    mode = Unicode('navigate').tag(sync=True)
    _addlayer = Unicode('').tag(sync=True)
    start_time = Unicode('').tag(sync=True)
    end_time = Unicode('').tag(sync=True)
    _extent = Unicode('').tag(sync=True)
    _token_info = Unicode('').tag(sync=True)

    _arcgis_url = Unicode('').tag(sync=True)

    _swipe_div = Unicode('').tag(sync=True)

    def __init__(self, **kwargs):
        """Constructor of Map widget.
        Accepts the following keyword arguments:
        gis     The gis instance with which the map widget works, used for authentication, and adding secure layers and private items from that GIS
        item    webmap item from portal with which to initialize the map widget
        """
        super(MapView, self).__init__(**kwargs)
        self._click_handlers = widgets.CallbackDispatcher()
        self._draw_end_handlers = widgets.CallbackDispatcher()

        self.on_msg(self._handle_map_msg)

        self.basemaps = ["streets", "satellite", "hybrid", "topo", "gray", "dark-gray", "oceans", "national-geographic",
                         "terrain", "osm"]
        self._swipe_div = 'swipeDiv' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

        self._gis = kwargs.pop('gis', None)
        if self._gis is not None and self._gis._con._username is not None:  # not anonymous
            token_info = {
                "server": self._gis._con.baseurl.replace('http://', 'https://'),
                "tokenurl": (self._gis._con.baseurl +
                             'generateToken').replace('http://', 'https://'),
                "username": self._gis._con._username,
                "password": self._gis._con._password
            }
            self._token_info = json.dumps(token_info)
            # if self._gis.properties.portalName != 'ArcGIS Online':
            self._arcgis_url = self._gis._con.baseurl + 'content/items'

        self.item = kwargs.pop('item', None)
        if self.item is not None:
            if isinstance(self.item, WebMap):
                self.item = self.item.item
            if 'type' in self.item and self.item.type.lower() != 'web map':
                raise TypeError("item type must be web map")
            self.id = self.item.id

    def draw(self, shape, popup=None, symbol=None, attributes=None):
        """
        Draws a shape.

        Arguments:
        shape is one of ["circle", "downarrow", "ellipse", "extent", "freehandpolygon",
        "freehandpolyline", "leftarrow", "line", "multipoint", "point", "polygon", "polyline",
        "rectangle", "rightarrow", "triangle", "uparrow", or geometry dict object]

        popup is a dict containing "title" and "content" as keys that will be displayed
        when the shape is clicked

        symbol is a symbol specified in json format as described at http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000000n5000000
        a default symbol is used is one is not specified

        attributes is a dict containing name value pairs of fields and field values
        associated with the graphic.

        """
        if isinstance(shape, list) and len(shape) == 2:  # [lat, long] pair
            shape = {'x': shape[1], 'y': shape[0], "spatialReference": {"wkid": 4326}, 'type': 'point'}
        elif isinstance(shape, tuple):  # (lat, long) pair
            shape = {'x': shape[1], 'y': shape[0], "spatialReference": {"wkid": 4326}, 'type': 'point'}

        if isinstance(shape, FeatureSet):
            fset = shape
            for feature in fset.features:
                graphic = {
                    "geometry": feature.geometry,
                    "infoTemplate": popup,
                    "symbol": symbol,
                    "attributes": feature.attributes
                }
                self.mode = json.dumps(graphic)
        elif isinstance(shape, dict):
            graphic = {
                "geometry": shape,
                "infoTemplate": popup,
                "symbol": symbol,
                "attributes": attributes
            }
            self.mode = json.dumps(graphic)
            # print(json.dumps(graphic))
        else:
            self.mode = shape

    def add_layer(self, item, options=None):
        """
        Adds layers from the provided item
        """
        if isinstance(item, Layer):
            js_layer = item._lyr_dict
            if options is not None:
                js_layer.update({"options": json.dumps(options)})

            self._addlayer = json.dumps(js_layer)
        elif 'layers' in item:  # items as well as services
            if item.layers is None:
                raise RuntimeError('No layers accessible/available in this item or service')
            for lyr in item.layers:
                js_layer = lyr._lyr_dict
                if options is not None:
                    js_layer.update({"options": json.dumps(options)})
                self._addlayer = json.dumps(js_layer)
        else:  # dict {'url':'xxx', 'type':'yyy', 'opacity':'zzz' ...}
            if options is not None:
                item.update({"options": json.dumps(options)})

            self._addlayer = json.dumps(item)

    def clear_graphics(self):
        self.mode = "###clear_graphics"

    def set_time_extent(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time

    def remove_layers(self):
        self.mode = "###remove_layers"

    @property
    def extent(self):
        return json.loads(self._extent)

    @extent.setter
    def extent(self, value):
        self._extent = json.dumps(value)

    def on_click(self, callback, remove=False):
        """Register a callback to execute when the map is clicked.

        The callback will be called with one argument,
        the clicked widget instance.

        Parameters
        ----------
        remove : bool (optional)
            Set to true to remove the callback from the list of callbacks."""
        self._click_handlers.register_callback(callback, remove=remove)

    def on_draw_end(self, callback, remove=False):
        """Register a callback to execute when something is drawn

        The callback will be called with two argument,
        the clicked widget instance, and the geometry drawn

        Parameters
        ----------
        remove : bool (optional)
            Set to true to remove the callback from the list of callbacks."""
        self._draw_end_handlers.register_callback(callback, remove=remove)

    # def _handle_map_msg(self, _, content):
    def _handle_map_msg(self, _, content, buffers):
        """Handle a msg from the front-end.

        Parameters
        ----------
        content: dict
            Content of the msg."""

        if content.get('event', '') == 'mouseclick':
            self._click_handlers(self, content.get('message', None))
        if content.get('event', '') == 'draw-end':
            self._draw_end_handlers(self, content.get('message', None))