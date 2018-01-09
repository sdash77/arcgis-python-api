"""
Mapping Holds the Plot function for creating a FeatureCollection JSON plus the render options
"""

import arcgis
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
def plot(df,
         renderer_type=None,
         col=None,
         palette='jet',
         alpha=1,
         line_width=1,
         marker='o',
         marker_size=10,
         **kwargs):
    """
    """
    if col is None and renderer_type is None:
        renderer_type = 's' # simple (default)
    elif col  not in df.columns:
        raise ValueError("Columns %s does not exist." % col)
    elif col and renderer_type is None:
        values = df[col].unique().tolist()
        renderer_type = 'u'

    return