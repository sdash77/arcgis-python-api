"""
Mapping Holds the Plot function for creating a FeatureCollection JSON plus the render options
"""

import arcgis
from arcgis.features._data.geodataset.viz.renderer import render
from arcgis.features._data.geodataset.viz.symbol import create_symbol, display_colormaps, show_styles
from arcgis.features import SpatialDataFrame
from arcgis.features import FeatureCollection
from arcgis.features import FeatureSet
from arcgis.features._data.geodataset import GeoSeries

CLASSIFICATIONS = {

    "simple": {'renderer_type' : 'u'}, # simple
    "quantiles" : {'renderer_type' : 'u'}, # quantiles
    "Quantiles" : {'renderer_type' : 'u'},

}

CLASS_CMAPS = {
     'classless': 'Greys',
     'unique_values': 'Paired',
     'quantiles': 'hot_r',
     'fisher_jenks': 'hot_r',
     'equal_interval': 'hot_r',
     'hot_spot' : "hot_r"
}

"""
====================  =========================================================
**Argument**          **Description**
--------------------  ---------------------------------------------------------
df                    required SpatialDataFrame or GeoSeries. This is the data
                      to map.
--------------------  ---------------------------------------------------------
map_widget            optional WebMap object
--------------------  ---------------------------------------------------------
palette               optional string/dict.  Color mapping.  For simple renderer,
                      just provide a string.  For more robust renderers like
                      unique renderer, a dictionary can be given.
--------------------  ---------------------------------------------------------
classif               optional string. If provided, a map will be renderered
                      given a collection of default mapping schema for the data.
--------------------  ---------------------------------------------------------
marker_yoffset
--------------------  ---------------------------------------------------------
line_width
--------------------  ---------------------------------------------------------
outline_style
--------------------  ---------------------------------------------------------
outline_color
====================  =========================================================
"""
RENDERER_TYPES = {
    "s" : 'simple',#
    "u" : 'unique',#
    'h' : 'heatmap',#
    'c' : 'ClassBreaks',#
    #"p" : 'Predominance',
    'str' : 'Stretch',#
    't' : "Temporal",#
    'v' : "vector field"#
}
def plot(df,
         map_widget=None,
         name=None,
         renderer_type=None,
         symbol_type=None,
         symbol_style=None,
         col=None,
         palette='jet',
         alpha=1,
         **kwargs):
    """
    """
    r = None
    map_exists = True
    if symbol_type is None:
        symbol_type = 'simple'
    if name is None:
        import uuid
        name = uuid.uuid4().hex[:7]
    if map_widget is None:
        map_exists = False
        from arcgis.mapping import WebMap
        map_widget = WebMap()
    fc = df.to_feature_collection(name=name)
    if col is None and renderer_type is None:
        renderer_type = 's' # simple (default)
        r = render(sdf_or_series=df,
                   label=name,
                   symbol_type=symbol_type,
                   symbol_style=symbol_style,
                   render_type=renderer_type,
                   cmap=palette,
                   alpha=alpha,
                   **kwargs)
        fc.layer['layerDefinition']['drawingInfo']['renderer'] = r
    elif col  not in df.columns:
        raise ValueError("Columns %s does not exist." % col)
    elif renderer_type == 's':
        renderer_type = 's'

    elif col and renderer_type is None:
        values = df[col].unique().tolist()
        renderer_type = 'u'
    if map_exists:
        map_widget.add_layer(layer=fc)
    else:
        map_widget.add_layer(layer=fc)
        return map_widget


if __name__ == "__main__":
    df = SpatialDataFrame.from_featureclass(r"D:\GIS\gp\schema.gdb\test_pts")
    wm = plot(df=df)
    print()