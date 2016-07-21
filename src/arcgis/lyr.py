"""
The arcgis.lyr module is used for accessing layers
"""
from __future__ import absolute_import
import json
import arcgis.gis
import collections
from pandas.io.json import json_normalize
from ._impl.service._layerfactory import Layer
__all__ = ['Layer', 'FeatureCollection']
###########################################################################
class FeatureCollection(collections.OrderedDict):
    """
    """
    def __init__(self, dictdata):
        """
        Constructs a feature collection given it's data
        """
        if isinstance(dictdata, arcgis.gis.Item):
            fcdict = dictdata.get_data()
            collections.OrderedDict.__init__(self, fcdict)
        else:
            fcdict = dictdata
            collections.OrderedDict.__init__(self, fcdict)

    def __str__(self):
        return json.dumps(self)

    def to_df(self):
        if 'layers' in self:
            df = json_normalize(self['layers'][0]['featureSet']['features'])
        else:
            df = json_normalize(self['featureSet']['features'])

        df.columns = df.columns.str.replace('attributes.', '')
        return df
