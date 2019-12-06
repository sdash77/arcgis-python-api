"""

This collection of tests ensures that the functionality in the arcgis api works
properly with the Spatially enabled DataFrame.

"""
import pytest
import os, sys
#sys.path.append(r"D:\SVN\git_hub\ArcGIS\geo_public")
import shutil, datetime
import tempfile
from arcgis.gis import GIS
from arcgis.features.geo._array import GeoArray, GeoType
from arcgis.features.geo import from_featureclass
from arcgis.geometry import Geometry
import copy
from arcgis.features.geo import _io
import pandas as pd
from pandas.core.internals import ExtensionBlock
import pandas.util.testing as tm

USERNAME = None
PASSWORD = None

_fs_dict = {
 "objectIdFieldName": "objectid",
 "globalIdFieldName": "globalid",
 "geometryType": "esriGeometryPoint",
 "spatialReference": {
  "wkid": 102100,
  "latestWkid": 3857
 },
 "fields": [
  {
   "name": "objectid",
   "alias": "OBJECTID",
   "type": "esriFieldTypeOID"
  },
  {
   "name": "requestid",
   "alias": "Service Request ID",
   "type": "esriFieldTypeString",
   "length": 25
  },
  {
   "name": "requesttype",
   "alias": "Problem",
   "type": "esriFieldTypeString",
   "length": 100
  },
  {
   "name": "comments",
   "alias": "Comments",
   "type": "esriFieldTypeString",
   "length": 255
  },
  {
   "name": "name",
   "alias": "Name",
   "type": "esriFieldTypeString",
   "length": 150
  },
  {
   "name": "phone",
   "alias": "Phone Number",
   "type": "esriFieldTypeString",
   "length": 12
  },
  {
   "name": "email",
   "alias": "Email Address",
   "type": "esriFieldTypeString",
   "length": 100
  },
  {
   "name": "requestdate",
   "alias": "Date Submitted",
   "type": "esriFieldTypeDate",
   "length": 36
  },
  {
   "name": "status",
   "alias": "Status",
   "type": "esriFieldTypeString",
   "length": 50
  },
  {
   "name": "globalid",
   "alias": "GlobalID",
   "type": "esriFieldTypeGlobalID",
   "length": 38
  },
  {
   "name": "building",
   "alias": "Building Name",
   "type": "esriFieldTypeString",
   "length": 25
  },
  {
   "name": "floor",
   "alias": "Floor Number",
   "type": "esriFieldTypeString",
   "length": 5
  }
 ],
 "features": [
  {
   "geometry": {
    "x": -9809161.170230601,
    "y": 5123045.5266209831
   },
   "attributes": {
    "objectid": 246362,
    "requestid": "69",
    "requesttype": "Sidewalk Damage",
    "comments": "Pothole",
    "name": "Foo Bar",
    "phone": "999-9999",
    "email": "foo@foobar.com",
    "requestdate": 1412921609000,
    "status": "Closed",
    "globalid": "{1776024F-0CA5-404E-A133-D442FB6FC0FE}",
    "building": "",
    "floor": ""
   }
  },
  {
   "geometry": {
    "x": -9074857.9234435894,
    "y": 4982391.2604217697
   },
   "attributes": {
    "objectid": 246382,
    "requestid": None,
    "requesttype": "Pothole",
    "comments": "Jhh",
    "name": "Foo Bar",
    "phone": None,
    "email": None,
    "requestdate": None,
    "status": "Unassigned",
    "globalid": "{B424A195-1EC8-4467-AE7E-24BE0EF74383}",
    "building": None,
    "floor": None
   }
  }
 ]
}


# -------------------------------------------------------------------------
def test_content_import_data():
    """
    tests the content.import_data works with the spatially enabled dataframe.
    """
    try:
    
        df = from_featureclass(filename=r"./world30.shp")
        gis = GIS(username=USERNAME, password=PASSWORD)
        item = gis.content.import_data(df)
        assert item.type == 'Feature Service'
        assert len(item.layers) > 0
        fgdb = item.related_items('Service2Data', direction='forward')[0]
        item.delete()
        fgdb.delete()
    except:
        pass
# -------------------------------------------------------------------------
def test_featureset_df():
    """tests the featurelayer.query method"""
    from arcgis.features import FeatureSet
    fs = FeatureSet.from_dict(_fs_dict)
    df = fs.sdf
    assert df.spatial._name == 'SHAPE'
    assert hasattr(df, 'spatial')
    assert hasattr(df.SHAPE, 'geom')
# -------------------------------------------------------------------------
def test_gp():
    from arcgis.features import FeatureSet
    gis = GIS()
    fs = FeatureSet.from_dict(_fs_dict)
    df = fs.sdf
    from arcgis.geoprocessing import import_toolbox
    vs = import_toolbox('http://sampleserver1.arcgisonline.com/ArcGIS/rest/services/Elevation/ESRI_Elevation_World/GPServer')
    import arcgis
    arcgis.env.out_spatial_reference = 4326
    res = vs.viewshed(df, "5 Miles") # "5 Miles" or LinearUnit(5, 'Miles') can be passed as input
    assert isinstance(res, FeatureSet)
    assert len(res) > 0


if __name__ == "__main__":
    print("Begin Integration Testing with Python API")
    if USERNAME and PASSWORD:
        print("################################################################")
        print("   Testing content.import_data")
        test_content_import_data()
        print("   Testing content.import_data finished")
        print("################################################################")
        print("   Testing GeoEnrichment")
        test_enrichment()
        print("   Testing GeoEnrichment finished")
    print("################################################################")
    print("   Testing FeatureSet.sdf")
    test_featureset_df()
    print("   Testing FeatureSet.sdf finished")

    print("################################################################")
    print("   Testing GP")
    test_gp()
    print("   Testing GP finished")
    print("################################################################")