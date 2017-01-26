"""
   Converts a Layer to a Pandas' DataFrame
"""
from __future__ import print_function
from __future__ import division
import arcgis.data.geodataset as gm
from arcgis.data.geodataset.utils import chunks
import json
import warnings
try:
    import arcgis
    HASARCGIS = True
except ImportError:
    warnings.warn("arcgis module is not installed cannot use this module")
    HASARCGIS = False
#--------------------------------------------------------------------------
def from_layer(service):
    """
    Converts a Feature Service Layer to a Pandas' DataFrame
    """
    if HASARCGIS and \
       isinstance(service, arcgis.features.layer.FeatureLayer):
        df = gm.SpatialDataFrame
        count = service.query(return_count_only=True)
        results = []
        if count > 1000:
            oids = service.query(return_ids_only=True)
            for pt in chunks(oids, 750):
                del pt

        else:
            vals = service.query()
            print ('stop')
        return gm.SpatialDataFrame.from_dict([])
    else:
        raise ValueError("Input must be of type FeatureLayer")
    raise NotImplementedError("from_layer not implemented")
#--------------------------------------------------------------------------
def to_layer(df, service):
    """
    Converts a Spatial DataFrame data and pushes it to a Feature Service
    Layer
    """
    if HASARCGIS and \
       isinstance(service, arcgis.features.layer.FeatureLayer) and \
       isinstance(df, arcgis.SpatialDataFrame):
        pass
    raise NotImplementedError("to_layer not implemented")
