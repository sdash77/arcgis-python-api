"""
Converts Esri JSON to and from a Spatial DataFrame.
"""
from __future__ import print_function
from __future__ import division
import json
try:
    import arcpy
    HASARCPY = True
except ImportError:
    HASARCPY = False
from fileops import to_featureclass
#----------------------------------------------------------------------
def from_json(json_text):
    """"""
    return
#----------------------------------------------------------------------
def to_json(df, out_path, out_name, overwrite=True):
    """"""
    return

