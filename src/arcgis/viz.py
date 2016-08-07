from __future__ import absolute_import
import arcgis.gis
import json
import os
import tempfile
import collections
import random
import string
from contextlib import contextmanager

from arcgis.tools import *
from arcgis.lyr import Layer, FeatureCollection
#from IPython.html import widgets
#from IPython.utils.traitlets import Unicode, Int, List
try:
    from ipywidgets import widgets
except:
    from IPython.html import widgets
#from IPython.html import widgets
try:
    from traitlets import Unicode, Int, List
except:
    from IPython.utils.traitlets import Unicode, Int, List


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
        webmapdict = self.item.get_data()
        collections.OrderedDict.__init__(self, webmapdict)
        #dict.update(webmapdict)

    def _repr_html_(self):
        #return '<iframe width=810 height=600 src="'+"http://developers.arcgis.com/javascript/samples/mobile_arcgis/?webmap="+self.item.itemid+'"/>'
        return '<iframe width=960 height=600 src="'+self.item._portal.url  + "/home/webmap/viewer.html?webmap=" + self.item.itemid + '"/>'

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
        with _tempinput(self.__str__()) as tempfilename:
            self.item.update(data=tempfilename)

class MapView(widgets.DOMWidget):
    _view_name = Unicode('MapView').tag(sync=True)
    _view_module = Unicode('mapview').tag(sync=True)

    value = Unicode('Hello World!').tag(sync=True)

    basemap = Unicode('topo').tag(sync=True)
    width = Unicode('100%').tag(sync=True)
    zoom = Int(2).tag(sync=True)
    id = Unicode('').tag(sync=True)
    center = List([0, 0]).tag(sync=True)
    mode = Unicode('navigate').tag(sync=True)
    addlayer = Unicode('').tag(sync=True)
    start_time = Unicode('').tag(sync=True)
    end_time = Unicode('').tag(sync=True)
    _swipe_div = Unicode('').tag(sync=True)

    def __init__(self, **kwargs):
        """Constructor"""
        super(MapView, self).__init__(**kwargs)
        self._click_handlers = widgets.CallbackDispatcher()
        self._draw_end_handlers = widgets.CallbackDispatcher()

        self.on_msg(self._handle_map_msg)

        self.basemaps = ["streets", "satellite", "hybrid", "topo", "gray", "dark-gray", "oceans", "national-geographic", "terrain", "osm"]
        self._swipe_div = 'swipeDiv' +''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        self.item = kwargs.pop('item', None)
        if self.item is not None:
            if self.item.type.lower() != 'web map':
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

        if isinstance(shape, dict):
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

            self.addlayer = json.dumps(js_layer)
        elif 'layers' in item: # items as well as services
            for lyr in item.layers:
                js_layer = lyr._js_lyr
                if options is not None:
                    js_layer.update({ "options" : json.dumps(options) })
                self.addlayer = json.dumps(js_layer)
        else: # dict {'url':'xxx', 'type':'yyy', 'opacity':'zzz' ...}
            if options is not None:
                item.update({ "options" : json.dumps(options) })

            self.addlayer = json.dumps(item)

            #layer = item
            ''' { 
                "type" : item['type'], 
                "url" : item['url'],
                "definition_expression" : item['definition_expression']
                "opacity" : 0.75
                }
            '''
            #self.addlayer = json.dumps(layer)
 
        """
        elif isinstance(item, arcgis.gis.Item):
            if item.type.lower() == 'feature service':
                fs = Layer(item)
                lyr_url = ""
                for layer in fs.layers:
                    lyr_url = layer['url']
                    #if it's from this portal, only then add token...
                    try:
                        if 'access' in item and item['access'] != 'public':
                            lyr_url = layer['url'] + "?token=" + item._portal.con.token
                    except:
                        pass
                    
                    js_layer = {
                        "type" : "FeatureLayer",
                        "url" : lyr_url
                        }
                    if options is not None:
                        js_layer.update({ "options" : json.dumps(options) })

                    self.addlayer = json.dumps(js_layer)
            
            elif item.type.lower() == 'feature collection':
                fcdict = item.get_data()
                fc = FeatureCollection(fcdict['layers'][0])
                #layer = fcdict['layers'][0]

                if options is not None:
                    fc.update({ "options" : json.dumps(options) })

                self.addlayer = json.dumps(fc)

            elif item.type.lower() == 'image service':
                layer = Layer(item)
                lyr_url = layer['url']
                try:
                    if 'access' in item and item['access'] != 'public':
                        lyr_url = layer['url'] + "?token=" + item._portal.con.token
                except:
                    pass
                
                js_layer = {
                    "type" : "ImageLayer",
                    "url" : lyr_url
                    }
                if options is not None:
                    js_layer.update({ "options" : json.dumps(options) })

                self.addlayer = json.dumps(js_layer)
            else:
                raise TypeError("item type must be feature service or image service")


        elif isinstance(item, FeatureService):
            for layer in item.layers:
                lyr_url = ""
                try:
                    if 'access' in item and item['access'] != 'public':
                        lyr_url = layer['url'] + "?token=" + item.item._portal.con.token
                except:
                    pass
                
                js_layer = {
                    "type" : "FeatureLayer",
                    "url" : lyr_url
                    }
                if options is not None:
                    js_layer.update({ "options" : json.dumps(options) })

                self.addlayer = json.dumps(js_layer)

        elif isinstance(item, FeatureCollection):
            if options is not None:
                item.update({ "options" : json.dumps(options) })

            self.addlayer = json.dumps(item)

        
        
        elif isinstance(item, ImageLayer):
            layer = {
                "type" : "ImageLayer",
                "url" : item['url']
                }
            if options is not None:
                layer.update({ "options" : json.dumps(options) })

            self.addlayer = json.dumps(layer)

        """

    def clear_graphics(self):
        self.mode = "###clear_graphics"

    def set_time_extent(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time

    def remove_layers(self):
        self.mode = "###remove_layers"


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
