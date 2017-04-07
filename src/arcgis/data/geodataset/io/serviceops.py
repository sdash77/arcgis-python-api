"""
   Converts a Layer to a Spatial DataFrame
"""
from __future__ import print_function
from __future__ import division
from .. import SpatialDataFrame
from arcgis.features.layer import FeatureLayer, Table
import pandas as pd
import json
import warnings
#--------------------------------------------------------------------------
def from_layer(layer):
    """
    Converts a Feature Service Layer to a Pandas' DataFrame

    Parameters:
     :layer: FeatureLayer or Table object.  If the object is a FeatureLayer
      the function will return a Spatial DataFrame, if the object is of
      type Table, the function will return a Pandas' DataFrame

    Usage:
    >>> from arcgis.arcgisserver import Layer
    >>> from arcgis import from_layer
    >>> mylayer = Layer("https://sampleserver6.arcgisonline.com/arcgis/rest" +\
                        "/services/CommercialDamageAssessment/FeatureServer/0")
    >>> sdf = from_layer(mylayer)
    >>> print(sdf)
    """
    if isinstance(layer, (Table, FeatureLayer)) == False:
        raise ValueError("Invalid inputs: must be FeatureLayer or Table")

    res = layer.query().df
    res.reset_index(drop=True, inplace=True)
    return res
