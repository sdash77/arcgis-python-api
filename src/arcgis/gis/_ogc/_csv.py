import os
import sys
import json
import uuid
import tempfile
from arcgis.gis import GIS, Item
from arcgis import env as _env
import pandas as pd
_PD_LESS_THAN1 = [int(v) for v in pd.__version__.split(".")] < [1,0,0]
###########################################################################
class CSVLayer(object):
    """
    Represents a CSV File Hosted on a Server.

    ===============     ====================================================================
    **Argument**        **Description**
    ---------------     --------------------------------------------------------------------
    url                 Required string. The administration URL for the ArcGIS Server.
    ---------------     --------------------------------------------------------------------
    gis                 Optional GIS. The `GIS` connection object
    ---------------     --------------------------------------------------------------------
    title               Optional String. The title of the layer used to identify it in places such as the Legend and LayerList widgets.
    ---------------     --------------------------------------------------------------------
    copyright           Optional String. Describes limitations and usage of the data.
    ---------------     --------------------------------------------------------------------
    id                  Optional String. The unique ID of the layer.
    ---------------     --------------------------------------------------------------------
    delimiter           Optional String. The separator value. This can be the following:
                        `,` (comma), ` ` (space), `|` (pipe), `\r` (tab), or `;` (semicolon).
    ---------------     --------------------------------------------------------------------
    sql_expression      Optional String. Optional query string to apply to the layer when displayed on the widget or web map.
    ---------------     --------------------------------------------------------------------
    fields              Optional List. An array of dictionarys containing the field information.
    ===============     ====================================================================

    """
    _url = None
    _gis = None
    _data = None
    _nrows = 15 #default number of rows to peak at.
    _id = None
    _renderer = None
    _latitude = None
    _longitude = None
    #----------------------------------------------------------------------
    def __init__(self, url_or_item, gis=None, **kwargs):
        """initializer"""
        if isinstance(url_or_item, str):
            self._url = url_or_item
            self._item = None
        elif isinstance(url_or_item, Item):
            self._item = url_or_item
            self._url = None
            if gis is None:
                gis = self._item._gis
        self._gis = gis or _env.active_gis or GIS()
        self._copyright = kwargs.pop('copyright', None)
        self._delimiter = kwargs.pop('delimiter', ',')
        self._fields = kwargs.pop('fields', None)
        self._sql = kwargs.pop('sql_expression', None)
        self._id = kwargs.pop('id', uuid.uuid4().hex)
        self._title = kwargs.pop('title', None)
        self._min_scale, self._max_scale = kwargs.pop('scale', (0,0))
        self._opacity = kwargs.pop('opacity', 0)
    #----------------------------------------------------------------------
    def __str__(self):
        if self._item:
            return f"<CSV @ {self._item.itemid}>"
        return f"<CSV @ {self._url}>"
    #----------------------------------------------------------------------
    def __repr__(self):
        return self.__str__()
    #----------------------------------------------------------------------
    @property
    def title(self):
        """
        Gets/Sets the Title of the Layer

        :returns: String
        """
        if self._title is None and self._url:
            self._title = os.path.basename(self._url)
        elif self._title is None and self._item:
            self._title = self._item.title
        return self._title
    #----------------------------------------------------------------------
    @title.setter
    def title(self, value):
        """
        Gets/Sets the Title of the Layer

        :returns: String
        """
        if value != self.title:
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
    def latitude(self):
        """
        The latitude field name. If not specified, the class will look for
        following field names in the CSV source: "lat", "latitude",
        "y", "ycenter", "latitude83", "latdecdeg", "POINT-Y".
        """
        auto_lat = ["lat", "latitude", "y",
                    "ycenter", "latitude83",
                    "latdecdeg", "point-y"]
        if self._latitude is None:
            for f in self.fields:
                if f['name'].lower() in auto_lat:
                    self._latitude = f['name']
                    break
        return self._latitude
    #----------------------------------------------------------------------
    @latitude.setter
    def latitude(self, value):
        if value != self._latitude and \
           value in [f['name'] for f in self.fields]:
            self._latitude = value
    #----------------------------------------------------------------------
    @property
    def longitude(self):
        """
        The longitude field name. If not specified, the `CSVLayer` will
        look for following field names in the CSV source: "lon", "lng",
        "long", "longitude", "x", "xcenter", "longitude83", "longdecdeg",
        "POINT-X".
        """
        auto_lat = ["lon", "lng",
                    "long", "longitude",
                    "x", "xcenter",
                    "longitude83", "longdecdeg",
                    "point-x"]
        if self._longitude is None:
            for f in self.fields:
                if f['name'].lower() in auto_lat:
                    self._longitude = f['name']
                    break
        return self._longitude
    #----------------------------------------------------------------------
    @longitude.setter
    def longitude(self, value):
        if value != self._longitude and \
           value in [f['name'] for f in self.fields]:
            self._longitude = value
    #----------------------------------------------------------------------
    @property
    def renderer(self):
        """
        Get/Set the Renderer of the CSV Layer

        :returns: InsensitiveDict

        """
        from arcgis._impl.common._isd import InsensitiveDict
        if self._renderer is None:
            from arcgis.mapping._viz import SimpleRenderer
            sr = SimpleRenderer(geometry_type="point")._to_dict()
            self._renderer = InsensitiveDict(dict(sr))
        return self._renderer
    #----------------------------------------------------------------------
    @renderer.setter
    def renderer(self, value):
        """
        Get/Set the Renderer of the CSV Layer

        :returns: InsensitiveDict

        """
        from arcgis._impl.common._isd import InsensitiveDict
        if isinstance(value, dict):
            self._renderer = InsensitiveDict(dict(value))
        elif value is None:
            self._renderer = None
        elif not isinstance(value, InsensitiveDict):
            raise ValueError("Invalid renderer type.")
        self._refresh = value

    #----------------------------------------------------------------------
    @property
    def delimiter(self):
        r"""
        Gets/Sets the delimiter for the CSV Layer.  The default is `,`

        ===========   ==========================================
        **Values**    **Description**
        -----------   ------------------------------------------
        ,             Comma
        -----------   ------------------------------------------
        " "           space
        -----------   ------------------------------------------
        ;             semicolon
        -----------   ------------------------------------------
        |             pipe
        -----------   ------------------------------------------
        `\r`          tab
        ===========   ==========================================

        :returns: string

        """
        if self._delimiter is None:
            self._delimiter = ","
        return self._delimiter
    #----------------------------------------------------------------------
    @delimiter.setter
    def delimiter(self, value):
        r"""
        Gets/Sets the delimiter for the CSV Layer.  The default is `,`

        ===========   ==========================================
        **Values**    **Description**
        -----------   ------------------------------------------
        ,             Comma
        -----------   ------------------------------------------
        " "           space
        -----------   ------------------------------------------
        ;             semicolon
        -----------   ------------------------------------------
        |             pipe
        -----------   ------------------------------------------
        `\r`          tab
        ===========   ==========================================

        :returns: string

        """
        if value in [',', ' ', ';', '|', '\r'] and \
           self._delimiter != value:
            self._delimiter = value
    #----------------------------------------------------------------------
    @property
    def copyright(self):
        """Copyright information for the layer."""
        return self._copyright
    #----------------------------------------------------------------------
    @copyright.setter
    def copyright(self):
        """Copyright information for the layer."""
        return self._copyright
    #----------------------------------------------------------------------
    @property
    def fields(self):
        """
        Returns the fields values for the CSV source.

        :returns: list of strings
        """
        import numpy as np
        import datetime
        if self._data is None and self._fields is None:
            fields = []
            self._data = self._df(True)
            for col in self._data.columns:
                try:
                    idx = self._data[col].first_valid_index()
                    col_val = self._data[col].loc[idx]
                except:
                    col_val = ""
                if isinstance(col_val, (str, np.str)):
                    fields.append({
                        "name" : col,
                        "type" : "string",
                        "alias" : col
                    })
                elif isinstance(col_val, (datetime.datetime,
                                          pd.Timestamp,
                                          np.datetime64,
                                          )):
                    fields.append({
                        "name" : col,
                        "type" : "date",
                        "alias" : col
                    })
                elif isinstance(col_val, (np.int32, np.int16, np.int8)):
                    fields.append({
                        "name" : col,
                        "type" : "long",
                        "alias" : col
                    })
                elif isinstance(col_val, (int, np.int, np.int64)):
                    fields.append({
                        "name" : col,
                        "type" : "integer",
                        "alias" : col
                    })
                elif isinstance(col_val, (float, np.float64)):
                    fields.append({
                        "name" : col,
                        "type" : "double",
                        "alias" : col
                    })
                elif isinstance(col_val, (np.float32)):
                    fields.append({
                        "name" : col,
                        "type" : "single",
                        "alias" : col
                    })
            self._fields = fields
        return self._fields
    #----------------------------------------------------------------------
    @property
    def sql_expression(self):
        """
        The SQL where clause used to filter features on the client. Only
        the features that satisfy the definition expression are displayed
        in the widget. Setting a definition expression is useful when the
        dataset is large and you don't want to bring all features to the
        client for analysis. The `sql_expressions` may be set when a
        layer is constructed prior to it loading in the view or after it
        has been loaded into the class.

        :return: String
        """
        return self._sql
    #----------------------------------------------------------------------
    @sql_expression.setter
    def sql_expression(self, value):
        """
        The SQL where clause used to filter features on the client. Only
        the features that satisfy the definition expression are displayed
        in the widget. Setting a definition expression is useful when the
        dataset is large and you don't want to bring all features to the
        client for analysis. The `sql_expressions` may be set when a
        layer is constructed prior to it loading in the view or after it
        has been loaded into the class.

        :return: String
        """
        if self._sql != value:
            self._sql = value
    #----------------------------------------------------------------------
    @property
    def _esri_json(self):
        """creates a dictionary for web map item."""
        add_layer =  {
            "type" : "csv",
            "delimiter" : self.delimiter,
            "copyright" : self.copyright or "",
            "definitionExpression" : self.sql_expression or "",
            "fields" : self.fields,
            "longitudeField" : self.longitude,
            "latitudeField" :self.latitude,
            'renderer' : self.renderer._json,
            'id' : self._id,
            'title' : self.title,
            'opacity' : self.opacity,
            'maxScale' : self.scale[1],
            'minScale' : self.scale[0]
        }
        if self._item:
            add_layer["portalItem"] = { "id" : self._item.itemid }
        else:
            add_layer["url"] = self._url
        return add_layer
    #----------------------------------------------------------------------
    def _df(self, glance=False):
        """returns the data as a pd.DataFrame"""
        if glance:
            nrows = self._nrows
        else:
            nrows = None
        if self._url:
            return pd.read_csv(self._url,
                                   sep=self.delimiter,
                                   nrows=nrows,
                                   infer_datetime_format=True,
                                   parse_dates=True)
        elif self._item:
            if self._item._gis._con.token:
                url = f"{self._item._gis._portal.resturl}content/items/{self._item.itemid}/data?token={self._item._gis._con.token}"
            else:
                url = f"{self._item._gis._portal.resturl}content/items/{self._item.itemid}/data"
            return pd.read_csv(url,
                               sep=self.delimiter,
                               nrows=nrows,
                               infer_datetime_format=True,
                               parse_dates=True)
        else:
            return None
    #----------------------------------------------------------------------
    @property
    def df(self):
        """
        returns the CSV file as a DataFrame

        :returns: Pandas' DataFrame
        """
        return self._df(False)


