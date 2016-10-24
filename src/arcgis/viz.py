from __future__ import absolute_import

import collections
import json
import os
import random
import string
import tempfile
from contextlib import contextmanager

from arcgis.lyr import Layer

#from IPython.html import widgets
#from IPython.utils.traitlets import Unicode, Int, List
try:
    from ipywidgets import widgets
except:
    from IPython.html import widgets
#from IPython.html import widgets
try:
    from traitlets import Unicode, Int, List, Bool
except:
    from IPython.utils.traitlets import Unicode, Int, List, Bool
__all__ = ["WebMap", "WebScene", "MapView"]

"""
The arcgis.viz module provides components for visualizing GIS data and analysis.
This module includes components such as MapView - an IPython Notebook widget for
working with maps, as well as WebMap and WebScene components that enable 2D and 3D
mapping and visualization in ArcGIS Online and on ArcGIS Portals.
"""

@contextmanager
def _tempinput(data):
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write((bytes(data, 'UTF-8')))
    temp.close()
    yield temp.name
    os.unlink(temp.name)

# pylint: disable=fixme, line-too-long
class WebMap(collections.OrderedDict):
    """
    Represents a webmap and provides access to it's basemaps and operational layers as well
    as functionality to visualize and interact with them.
    http://resources.arcgis.com/en/help/arcgis-web-map-json/index.html#/Web_map_format_overview/02qt00000007000000/
    """
    def __init__(self, webmapitem):
        """
        Constructs a Webmap object given it's item from ArcGIS Online or Portal.
        """
        if webmapitem.type.lower() != 'web map':
            raise TypeError("item type must be web map")
        self.item = webmapitem
        self._gis = webmapitem._gis
        self._con = self._gis._con
        webmapdict = self.item.get_data()
        collections.OrderedDict.__init__(self, webmapdict)
        #dict.update(webmapdict)

    #def _repr_html_(self):
    def _ipython_display_(self, **kwargs):
        #return '<iframe width=960 height=600 src="'+self.item._portal.url  + "/home/webmap/viewer.html?webmap=" + self.item.itemid + '"/>'
        mapwidget = MapView(gis=self._gis, item=self.item)
        return mapwidget._ipython_display_(**kwargs)

    #def __repr__(self):
    #    dictrepr = collections.OrderedDict.__repr__(self)
    #    return '%s(%s)' % (type(self).__name__, dictrepr)

    def __str__(self):
        return json.dumps(self)

    def update(self):
        #with _tempinput(self.__str__()) as tempfilename:
        self.item.update({ 'text':self.__str__() })

class WebScene(collections.OrderedDict):
    """
    Represents a web scene and provides access to it's basemaps and operational layers as well
    as functionality to visualize and interact with them.
    """

    def __init__(self, websceneitem):
        """
        Constructs a WebScene object given it's item from ArcGIS Online or Portal.
        """
        if websceneitem.type.lower() != 'web scene':
            raise TypeError("item type must be web scene")
        self.item = websceneitem
        webscenedict = self.item.get_data()
        collections.OrderedDict.__init__(self, webscenedict)

    def _repr_html_(self):
        return '<iframe width=960 height=600 src="'+"http://www.arcgis.com/home/webscene/viewer.html?webscene="+self.item.itemid+'"/>'

    #def __repr__(self):
    #    dictrepr = dict.__repr__(self)
    #    return '%s(%s)' % (type(self).__name__, dictrepr)

    def __str__(self):
        return json.dumps(self)

    def update(self):
        #with _tempinput(self.__str__()) as tempfilename:
        self.item.update({ 'text':self.__str__() })

class MapView(widgets.DOMWidget):
    _view_name = Unicode('MapView').tag(sync=True)
    _view_module = Unicode('mapview').tag(sync=True)

    #value = Unicode('Hello World!').tag(sync=True)

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

        self.basemaps = ["streets", "satellite", "hybrid", "topo", "gray", "dark-gray", "oceans", "national-geographic", "terrain", "osm"]
        self._swipe_div = 'swipeDiv' +''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        
        self._gis = kwargs.pop('gis', None)
        if self._gis is not None and self._gis._con._username is not None: # not anonymous
            token_info = {
                "server" : self._gis._con.baseurl.replace('http://', 'https://'),
                "tokenurl" : (self._gis._con.baseurl + 
                               'generateToken').replace('http://', 'https://'),
                "username" : self._gis._con._username,
                "password" : self._gis._con._password
            }
            self._token_info = json.dumps(token_info)
            #if self._gis.properties.portalName != 'ArcGIS Online':
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
        if isinstance(shape, list) and len(shape) == 2: # [lat, long] pair
            shape = { 'x':shape[1], 'y':shape[0], "spatialReference": {"wkid":4326}, 'type':'point' }
        elif isinstance(shape, tuple): # (lat, long) pair
            shape = { 'x':shape[1], 'y':shape[0], "spatialReference": {"wkid":4326}, 'type':'point' }

        if isinstance(shape, FeatureSet):
            fset = shape
            for feature in fset.features:
                graphic = {
                    "geometry" : feature.geometry,
                    "infoTemplate" : popup,
                    "symbol" : symbol,
                    "attributes" : feature.attributes
                }
                self.mode = json.dumps(graphic)
        elif isinstance(shape, dict):
            graphic = {
                "geometry" : shape,
                "infoTemplate" : popup,
                "symbol" : symbol,
                "attributes" : attributes
            }
            self.mode = json.dumps(graphic)
            #print(json.dumps(graphic))
        else:
            self.mode = shape

    def add_layer(self, item, options=None):
        """
        Adds layers from the provided item
        """
        if isinstance(item, Layer):
            js_layer = item._js_lyr
            if options is not None:
                js_layer.update({ "options" : json.dumps(options) })

            self._addlayer = json.dumps(js_layer)
        elif 'layers' in item: # items as well as services
            if item.layers is None:
                raise RuntimeError('No layers accessible/available in this item or service')
            for lyr in item.layers:
                js_layer = lyr._js_lyr
                if options is not None:
                    js_layer.update({ "options" : json.dumps(options) })
                self._addlayer = json.dumps(js_layer)
        else: # dict {'url':'xxx', 'type':'yyy', 'opacity':'zzz' ...}
            if options is not None:
                item.update({ "options" : json.dumps(options) })

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

    #def _handle_map_msg(self, _, content):
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
