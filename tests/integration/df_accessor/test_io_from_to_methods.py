import pytest
import os, sys
sys.path.append(r"C:\SVN\achapkowski_geosaurus_fork\src")
import shutil
import tempfile
import pandas as pd
from arcgis.features.geo import GeoAccessor, GeoSeriesAccessor
from arcgis.geometry import Geometry
from arcgis.gis import GIS
from arcgis.geometry import Geometry

##--------------------------------------------------------------------------
##
##   Module serviceops.py Testing
##
##   This tests the serviceops.py module. This includes to_featureset,
##   from_layer, to_layer and _chunks methods
##
##--------------------------------------------------------------------------
from arcgis.features.geo._io.serviceops import _chunks, to_featureset, to_layer, from_layer
#--------------------------------------------------------------------------
def test_chunks():
    """Tests the chunking method"""
    sizes = []
    l = [0] * 100
    n = 50
    count = 0
    for i in _chunks(l,n):
        sizes.append(len(i) == 50)
        count += 1
    assert count == 2
    assert all(sizes)
#--------------------------------------------------------------------------
def test_from_layer():
    """tests the from_layer method"""
    item_id = "01c4d9bf9c7a4ad79ec7bd7afa0c2316"
    where = """CNTRY_NAME = 'San Marino'"""
    gis = GIS(verify_cert=False)
    lyr = gis.content.get('6996f03a1b364dbab4008d99380370ed').layers[0]
    df = from_layer(lyr, where)
    #print(df)
    #print(df.head())
    assert len(df) == 1
    assert 'SHAPE' in df.columns
    #assert all((df.SHAPE.geom.area > 0).tolist())
    #assert df.spatial.area > 0
    #assert df.SHAPE.geom.centroid.name == 'centroid'
##--------------------------------------------------------------------------
#def test_to_layer():
    #""" tests the to_layer operation"""
    #from arcgis.features import FeatureLayer
    #gis = GIS(verify_cert=False)
    #lyr = gis.content.get('6996f03a1b364dbab4008d99380370ed').layers[0]
    #where = """CNTRY_NAME = 'San Marino'"""
    #df = from_layer(lyr, where)
    #df['FIPS_CNTRY'] = "QM"
    #layer = to_layer(df, layer=lyr, update_existing=True)
    #assert isinstance(layer, FeatureLayer)
    #assert layer.query(where).sdf['FIPS_CNTRY'][0] == 'QM'
    #df['FIPS_CNTRY'] = "SM"
    #layer = to_layer(df, layer=lyr, update_existing=True)
    #assert layer.query(where).sdf['FIPS_CNTRY'][0] == 'SM'
#--------------------------------------------------------------------------

def test_from_gpd_df_sanity():
    """
    Sanity test case, verifies can read GeoDataFrame to a SeDF
    :return:
    """
    import geopandas as gpd
    geo_df = gpd.read_file('./world30.shp')

    assert isinstance(geo_df, gpd.GeoDataFrame)

    world_sedf = pd.DataFrame.spatial.from_geodataframe(geo_df)

    assert isinstance(world_sedf, pd.DataFrame)
    print('Can successfully read GPD DF to SeDF')

# -------------------------------------------------------------------------

def test_to_gpd_df_sanity():
    """
    Sanity test case, verifies can export SeDF to GeoDataFrame
    :return:
    """
    import geopandas as gpd

    sedf = pd.DataFrame.spatial.from_featureclass('./world30.shp')
    assert isinstance(sedf, pd.DataFrame)

    # export
    geo_df = sedf.spatial.to_geodataframe()
    assert isinstance(geo_df, gpd.GeoDataFrame)

    print('Can successfully export SeDF to GPD')

if __name__ == "__main__":
    test_chunks()
    test_from_layer()
    test_from_gpd_df_sanity()
    test_to_gpd_df_sanity()
    #test_to_layer()  # SKIPPED