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

from configparser import ConfigParser
from pathlib import Path
from integration.dino_utils.dino_configs import DinoConfigs
##--------------------------------------------------------------------------
##
##   Module serviceops.py Testing
##
##   This tests the serviceops.py module. This includes to_featureset,
##   from_layer, to_layer and _chunks methods
##
##--------------------------------------------------------------------------
from arcgis.features.geo._io.serviceops import _chunks, to_featureset, to_layer, from_layer

# get data paths needed for the test cases
_conf_reader2 = ConfigParser()
_conf_reader2.read(DinoConfigs.root_init_file, 'UTF-8')

qalab_base_path = _conf_reader2['test_data']['qalab_base_path']
qalab_data_path = qalab_base_path + _conf_reader2['test_data']['qalab_dataprep']

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


def test_from_gpd_df_verify_crs_gcs_points():
    """
    Sanity test case, verifies can read GeoDataFrame to a SeDF
    :return:
    """
    import geopandas as gpd
    data_path = os.path.join(qalab_data_path, "spatial_ref_tests", "points_gcs_nad83.shp")
    geo_df = gpd.read_file(data_path)

    assert isinstance(geo_df, gpd.GeoDataFrame)
    assert geo_df.crs == {'init': 'epsg:4269'}
    assert geo_df.shape == (317,30)
    print(geo_df.columns)

    sedf = pd.DataFrame.spatial.from_geodataframe(geo_df)
    assert isinstance(sedf, pd.DataFrame)
    assert sedf.iloc[0]['SHAPE']['spatialReference'] == {'wkid': 4326}
    assert sedf.iloc[0]['SHAPE'].type == 'POINT'
    assert sedf.shape == (317, 30)
    assert 'SHAPE' in sedf.columns
    print(sedf.columns)

    print('GPD->SeDF Points GCS success')


def test_from_gpd_df_verify_crs_pcs_points():
    """
    Sanity test case, verifies can read GeoDataFrame to a SeDF
    :return:
    """
    import geopandas as gpd
    data_path = os.path.join(qalab_data_path, "spatial_ref_tests", "points_pcs_utm.shp")
    geo_df = gpd.read_file(data_path)

    assert isinstance(geo_df, gpd.GeoDataFrame)
    assert geo_df.crs['proj'] == 'utm'

    sedf = pd.DataFrame.spatial.from_geodataframe(geo_df)
    assert isinstance(sedf, pd.DataFrame)
    assert sedf.iloc[0]['SHAPE']['spatialReference'] == {'wkid': 4326}
    assert sedf.iloc[0]['SHAPE'].type == 'Point'
    assert 'SHAPE' in sedf.columns
    assert 'OBJECTID' in sedf.columns

    print('GPD->SeDF Points PCS success')


def test_from_gpd_df_verify_crs_gcs_lines():
    """
    Sanity test case, verifies can read GeoDataFrame to a SeDF
    :return:
    """
    import geopandas as gpd
    data_path = os.path.join(qalab_data_path, "spatial_ref_tests", "lines_gcs_wgs84.shp")
    geo_df = gpd.read_file(data_path)

    assert isinstance(geo_df, gpd.GeoDataFrame)
    assert geo_df.crs['init'] == 'epsg:4326'

    sedf = pd.DataFrame.spatial.from_geodataframe(geo_df)
    assert isinstance(sedf, pd.DataFrame)
    assert sedf.iloc[0]['SHAPE']['spatialReference'] == {'wkid': 4326}
    assert sedf.iloc[0]['SHAPE'].type == 'Polyline'
    assert 'SHAPE' in sedf.columns
    assert 'OBJECTID' in sedf.columns

    print('GPD->SeDF Lines GCS success')

def test_from_gpd_df_verify_crs_pcs_lines():
    """
    Sanity test case, verifies can read GeoDataFrame to a SeDF
    :return:
    """
    import geopandas as gpd
    data_path = os.path.join(qalab_data_path, "spatial_ref_tests", "lines_pcs_wgs84_webmerc.shp")
    geo_df = gpd.read_file(data_path)

    assert isinstance(geo_df, gpd.GeoDataFrame)
    assert geo_df.crs['init'] == 'epsg:3857'

    sedf = pd.DataFrame.spatial.from_geodataframe(geo_df)
    assert isinstance(sedf, pd.DataFrame)
    assert sedf.iloc[0]['SHAPE']['spatialReference'] == {'wkid': 4326}
    assert sedf.iloc[0]['SHAPE'].type == 'Polyline'
    assert 'SHAPE' in sedf.columns
    assert 'OBJECTID' in sedf.columns

    print('GPD->SeDF Lines PCS success')

def test_from_gpd_df_verify_crs_gcs_polygons():
    """
    Sanity test case, verifies can read GeoDataFrame to a SeDF
    :return:
    """
    import geopandas as gpd
    data_path = os.path.join(qalab_data_path, "spatial_ref_tests", "polygons_gcs_wgs84.shp")
    geo_df = gpd.read_file(data_path)

    assert isinstance(geo_df, gpd.GeoDataFrame)
    assert geo_df.crs['init'] == 'epsg:4326'

    sedf = pd.DataFrame.spatial.from_geodataframe(geo_df)
    assert isinstance(sedf, pd.DataFrame)
    assert sedf.iloc[0]['SHAPE']['spatialReference'] == {'wkid': 4326}
    assert sedf.iloc[0]['SHAPE'].type == 'Polygon'
    assert 'SHAPE' in sedf.columns
    assert 'OBJECTID' in sedf.columns

    print('GPD->SeDF Polygons GCS success')

def test_from_gpd_df_verify_crs_pcs_polygons():
    """
    Sanity test case, verifies can read GeoDataFrame to a SeDF
    :return:
    """
    import geopandas as gpd
    data_path = os.path.join(qalab_data_path, "spatial_ref_tests", "polygons_pcs_utm.shp")
    geo_df = gpd.read_file(data_path)

    assert isinstance(geo_df, gpd.GeoDataFrame)
    assert geo_df.crs['proj'] == 'utm'

    sedf = pd.DataFrame.spatial.from_geodataframe(geo_df)
    assert isinstance(sedf, pd.DataFrame)
    assert sedf.iloc[0]['SHAPE']['spatialReference'] == {'wkid': 4326}
    assert sedf.iloc[0]['SHAPE'].type == 'Polygon'
    assert 'SHAPE' in sedf.columns
    assert 'OBJECTID' in sedf.columns

    print('GPD->SeDF Polygons GCS success')

# def test_to_gpd_df_sanity():  # export to GeoDataFrame is disabled.
#     """
#     Sanity test case, verifies can export SeDF to GeoDataFrame
#     :return:
#     """
#     import geopandas as gpd
#
#     sedf = pd.DataFrame.spatial.from_featureclass('./world30.shp')
#     assert isinstance(sedf, pd.DataFrame)
#
#     # export
#     geo_df = sedf.spatial.to_geodataframe()
#     assert isinstance(geo_df, gpd.GeoDataFrame)
#
#     print('Can successfully export SeDF to GPD')

if __name__ == "__main__":
    test_chunks()
    test_from_layer()
    test_from_gpd_df_sanity()
    test_to_gpd_df_sanity()
    #test_to_layer()  # SKIPPED