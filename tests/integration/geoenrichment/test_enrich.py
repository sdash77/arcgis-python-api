from typing import Union, Iterable

from arcgis.features import FeatureSet
from arcgis.features.geo import _is_geoenabled
from arcgis.geometry import Point
from arcgis.geoenrichment import Country
from arcgis.geoenrichment._business_analyst._utils import pep8ify
import pandas as pd
import pytest

from .configtest import (
    does_not_raise,
    skip_if_no_local,
    skip_if_no_agol,
    usa_local,
    usa_local_enrich_vars,
    usa_agol,
    usa_agol_enrich_vars,
    polygon_df,
    line_df,
    point_df,
    stdgeo_srs,
)


# root tests
def enrich_test(enrich_src: Country, geom: Union[pd.DataFrame, pd.Series, Iterable],
                enrich_vars: Union[pd.DataFrame, list], expectation: object, std_geo_lvl: Union[str, int] = None,
                std_geo_id_col: str = None, prx_typ: str = None, prx_val: Union[int, float] = None,
                prx_mtrc: str = None) -> None:
    with expectation:

        enrich_res = enrich_src.enrich(geom, enrich_vars, standard_geography_level=std_geo_lvl,
                                       standard_geography_id_column=std_geo_id_col,
                                       proximity_type=prx_typ,
                                       proximity_value=prx_val,
                                       proximity_metric=prx_mtrc)

        assert isinstance(enrich_res, pd.DataFrame)

        assert enrich_res.spatial.validate()

        if isinstance(enrich_vars, list):
            enrich_vars = enrich_src._ba_cntry.get_enrich_variables_from_iterable(enrich_vars)
        enrich_var_cols = [pep8ify(val) for val in enrich_vars['name']]
        enrich_res_cols = list(enrich_res.columns)
        assert all([[enrich_col in enrich_res_cols] for enrich_col in enrich_var_cols])


def enrich_feature_set_test(enrich_src: Country, geom: Union[pd.DataFrame, FeatureSet],
                enrich_vars: Union[pd.DataFrame, list], expectation: object, std_geo_lvl: Union[str, int] = None,
                std_geo_id_col: str = None, prx_typ: str = None, prx_val: Union[int, float] = None,
                prx_mtrc: str = None) -> None:
    with expectation:

        if isinstance(geom, FeatureSet):
            geom = geom.spatial.to_featurset()

        enrich_res = enrich_src.enrich(geom, enrich_vars, standard_geography_level=std_geo_lvl,
                                       standard_geography_id_column=std_geo_id_col,
                                       proximity_type=prx_typ,
                                       proximity_value=prx_val,
                                       proximity_metric=prx_mtrc)

        assert isinstance(enrich_res, pd.DataFrame)

        assert enrich_res.spatial.validate()

        if isinstance(enrich_vars, list):
            enrich_vars = enrich_src._ba_cntry.get_enrich_variables_from_iterable(enrich_vars)
        enrich_var_cols = [pep8ify(val) for val in enrich_vars['name']]
        enrich_res_cols = list(enrich_res.columns)
        assert all([[enrich_col in enrich_res_cols] for enrich_col in enrich_var_cols])


def enrich_do_not_return_geom_test(enrich_src: Country, geom_df: pd.DataFrame,
                                   enrich_vars: Union[pd.DataFrame, list], expectation: object,
                                   std_geo_lvl: Union[str, int] = None, std_geo_id_col: str = None) -> None:
    with expectation:

        enrich_res = enrich_src.enrich(geom_df, enrich_vars, standard_geography_level=std_geo_lvl,
                                       standard_geography_id_column=std_geo_id_col, return_geometry=False)

        assert isinstance(enrich_res, pd.DataFrame)

        assert 'SHAPE' not in list(enrich_res.columns)

        assert enrich_res.spatial.validate() is False

        if isinstance(enrich_vars, list):
            enrich_vars = enrich_src._ba_cntry.get_enrich_variables_from_iterable(enrich_vars)
        enrich_var_cols = [pep8ify(val) for val in enrich_vars['enrich_field_name']]
        enrich_res_cols = list(enrich_res.columns)
        assert all([[enrich_col in enrich_res_cols] for enrich_col in enrich_var_cols])


def enrich_json_input_test(enrich_src: Country, enrich_vars: pd.DataFrame, expectation: object) -> None:

    with expectation:

        geom = [
            {"geometry": {
                "rings": [
                    [[-117.185412, 34.063170], [-122.81, 37.81], [-117.200570, 34.057196], [-117.185412, 34.063170]]
                ],
            "spatialReference": {"wkid": 4326}},
            "attributes": {"id": "1", "name": "optional polygon area name"}
            }
        ]

        enrich_res = enrich_src.enrich(geom, enrich_vars)

        if isinstance(enrich_vars, list):
            enrich_vars = enrich_src._ba_cntry.get_enrich_variables_from_iterable(enrich_vars)
        assert isinstance(enrich_res, pd.DataFrame)
        enrich_var_cols = [pep8ify(val) for val in enrich_vars['enrich_field_name']]
        enrich_res_cols = list(enrich_res.columns)
        assert all([[enrich_col in enrich_res_cols] for enrich_col in enrich_var_cols])


def enrich_geometry_list_test(enrich_src: Country, enrich_vars: Union[pd.DataFrame, list],
                              expectation: object = does_not_raise()) -> None:
    with expectation:
        geom_lst = [
            Point({"x": -122.435, "y": 37.785, "spatialReference": {"wkid": 4326}}),
            Point({"x": -122.433, "y": 37.734, "spatialReference": {"wkid": 4326}})
        ]

        enrich_res = enrich_src.enrich(geom_lst, enrich_variables=enrich_vars)

        assert isinstance(enrich_res, pd.DataFrame)

        if isinstance(enrich_vars, list):
            enrich_vars = enrich_src._ba_cntry.get_enrich_variables_from_iterable(enrich_vars)
        enrich_var_cols = [pep8ify(val) for val in enrich_vars['enrich_field_name']]
        enrich_res_cols = list(enrich_res.columns)
        assert all([[enrich_col in enrich_res_cols] for enrich_col in enrich_var_cols])


# local
@skip_if_no_local
def test_enrich_usa_poly_local(usa_local, polygon_df, usa_local_enrich_vars):
    enrich_test(usa_local, polygon_df, usa_local_enrich_vars, does_not_raise())


@skip_if_no_local
def test_enrich_usa_line_implicit_local(usa_local, line_df, usa_local_enrich_vars):
    enrich_test(usa_local, line_df, usa_local_enrich_vars, does_not_raise())


@skip_if_no_local
def test_enrich_usa_line_explicit_local(usa_local, line_df, usa_local_enrich_vars):
    enrich_test(usa_local, line_df, usa_local_enrich_vars, pytest.raises(AssertionError), prx_typ='driving_time')


@skip_if_no_local
def test_enrich_usa_point_straightline_implicit_local(usa_local, point_df, usa_local_enrich_vars):
    enrich_test(usa_local, point_df, usa_local_enrich_vars, does_not_raise())


@skip_if_no_local
def test_enrich_usa_point_straightline_explicit_local(usa_local, point_df, usa_local_enrich_vars):
    enrich_test(usa_local, point_df, usa_local_enrich_vars, does_not_raise(), prx_typ='straight_line')


@skip_if_no_local
def test_enrich_usa_point_drivedistance_local(usa_local, point_df, usa_local_enrich_vars):
    enrich_test(usa_local, point_df, usa_local_enrich_vars, does_not_raise(), prx_typ='driving_distance', prx_val=10,
                prx_mtrc='miles')


@skip_if_no_local
def test_enrich_usa_point_drivetime_local(usa_local, point_df, usa_local_enrich_vars):
    enrich_test(usa_local, point_df, usa_local_enrich_vars, does_not_raise(), prx_typ='driving_time', prx_val=12,
                prx_mtrc='minutes')


@skip_if_no_local
def test_enrich_usa_no_return_geomery_local(usa_local, polygon_df, usa_local_enrich_vars):
    enrich_do_not_return_geom_test(usa_local, polygon_df, usa_local_enrich_vars, does_not_raise())


@skip_if_no_local
def test_enrich_usa_stdgeo_srs_local(usa_local, stdgeo_srs, usa_local_enrich_vars):
    enrich_test(usa_local, stdgeo_srs.iloc[:10], usa_local_enrich_vars, does_not_raise(), std_geo_lvl='block_groups')


@skip_if_no_local
def test_enrich_usa_stdgeo_srs_no_return_geom_local(usa_local, stdgeo_srs, usa_local_enrich_vars):
    enrich_do_not_return_geom_test(usa_local, stdgeo_srs, usa_local_enrich_vars, does_not_raise(),
                                   std_geo_lvl='block_groups')


@skip_if_no_local
def test_enrich_usa_stdgeo_df_local(usa_local, polygon_df, usa_local_enrich_vars):
    polygon_df = polygon_df.drop(columns='SHAPE')
    enrich_test(usa_local, polygon_df, usa_local_enrich_vars, does_not_raise(), std_geo_lvl='block_groups',
                std_geo_id_col='ID')


@skip_if_no_local
def test_enrich_usa_variable_name_list_local(usa_local, polygon_df):
    enrich_test(usa_local, polygon_df, ["populationtotals.TOTPOP_CY", "AtRisk.TOTPOP_CY"], does_not_raise())


@skip_if_no_local
def test_enrich_usa_after_can_variable_name_list_local(usa_local, polygon_df):
    import arcpy
    arcpy.env.baDataSource = "LOCAL;;CAN_ESRI_2021"
    enrich_test(usa_local, polygon_df, ["populationtotals.TOTPOP_CY", "AtRisk.TOTPOP_CY"], does_not_raise())


@skip_if_no_local
def test_enrich_json_local(usa_local, usa_local_enrich_vars):
    enrich_json_input_test(usa_local, usa_local_enrich_vars, pytest.raises(ValueError))


# ArcGIS Online
@skip_if_no_agol
def test_enrich_usa_stdgeo_srs_usa_agol(usa_agol, stdgeo_srs, usa_agol_enrich_vars):
    enrich_test(usa_agol, stdgeo_srs, usa_agol_enrich_vars, does_not_raise(), std_geo_lvl='block_groups')


@skip_if_no_agol
def test_enrich_usa_stdgeo_srs_no_return_geom_agol(usa_agol, stdgeo_srs, usa_agol_enrich_vars):
    enrich_do_not_return_geom_test(usa_agol, stdgeo_srs, usa_agol_enrich_vars, does_not_raise(),
                                   std_geo_lvl='block_groups')


@skip_if_no_agol
def test_enrich_usa_stdgeo_df_agol(usa_agol, polygon_df, usa_agol_enrich_vars):
    polygon_df = polygon_df.drop(columns='SHAPE')
    enrich_test(usa_agol, polygon_df, usa_agol_enrich_vars, does_not_raise(), std_geo_lvl='block_groups',
                std_geo_id_col='ID')


@skip_if_no_agol
def test_enrich_usa_poly_singlebatch_agol(usa_agol, polygon_df, usa_agol_enrich_vars):
    polygon_df = polygon_df.iloc[:45]
    polygon_df.spatial.set_geometry('SHAPE')
    enrich_test(usa_agol, polygon_df, usa_agol_enrich_vars, does_not_raise())


@skip_if_no_agol
def test_enrich_usa_poly_agol(usa_agol, polygon_df, usa_agol_enrich_vars):
    enrich_test(usa_agol, polygon_df, usa_agol_enrich_vars, does_not_raise())


@skip_if_no_agol
def test_enrich_feature_set_usa_poly_agol(usa_agol, polygon_df, usa_agol_enrich_vars):
    enrich_feature_set_test(usa_agol, polygon_df, usa_agol_enrich_vars, does_not_raise())


@skip_if_no_agol
def test_enrich_usa_line_agol(usa_agol, line_df, usa_agol_enrich_vars):
    enrich_test(usa_agol, line_df, usa_agol_enrich_vars, does_not_raise())


@skip_if_no_agol
def test_enrich_usa_point_drivedistance_agol(usa_agol, point_df, usa_agol_enrich_vars):
    enrich_test(usa_agol, point_df, usa_agol_enrich_vars, does_not_raise(), prx_typ='drive_distance',
                prx_val=10, prx_mtrc='miles')


@skip_if_no_agol
def test_enrich_usa_point_drivetime_agol(usa_agol, point_df, usa_agol_enrich_vars):
    enrich_test(usa_agol, point_df, usa_agol_enrich_vars, does_not_raise(), prx_typ='drive_time',
                prx_val=12, prx_mtrc='minutes')


@skip_if_no_agol
def test_enrich_json_agol(usa_agol, polygon_df, usa_agol_enrich_vars):
    enrich_json_input_test(usa_agol, usa_agol_enrich_vars, does_not_raise())


@skip_if_no_agol
def test_enrich_usa_variable_name_list_agol(usa_agol, polygon_df):
    enrich_test(usa_agol, polygon_df, ["populationtotals.TOTPOP_CY", "AtRisk.TOTPOP_CY"], does_not_raise())


@skip_if_no_agol
def test_enrich_geometry_list_agol(usa_agol, usa_agol_enrich_vars):
    enrich_geometry_list_test(usa_agol, usa_agol_enrich_vars, does_not_raise())


@skip_if_no_agol
def test_enrich_buffer_multiple_addresses_agol(usa_agol, usa_agol_enrich_vars):

    with does_not_raise():
        address_lst = ['380 New York St, Redlands CA, 92373', '111 Market St, Olympia WA, 98501']
        enrich_res = usa_agol.enrich(address_lst, enrich_variables=usa_agol_enrich_vars)
        assert isinstance(enrich_res, pd.DataFrame)


@skip_if_no_agol
def test_enrich_large_json_no_enrich_vars(usa_agol):

    from arcgis.geoenrichment import enrich

    with does_not_raise():
        raw_json = [
                        {
                            "geometry": {"x": -122.435, "y": 37.785},
                            "attributes": {"id": "1"},
                        },
                        {
                            "geometry": {"x": -122.433, "y": 37.734},
                            "attributes": {"id": "2"},
                        },
                        {
                            "sourceCountry": "US",
                            "layer": "US.ZIP5",
                            "ids": ["92373", "92129"],
                        },
                        {
                            "geometry": {"x": -122.435, "y": 37.785},
                            "areaType": "NetworkServiceArea",
                            "bufferUnits": "Hours",
                            "bufferRadii": [1],
                            "travel_mode": "Driving",
                        },
                        {
                            "address": {
                                "text": "12 Concorde Place Toronto ON M3C 3R8",
                                "sourceCountry": "Canada",
                            }
                        },
                        {
                            "address": {
                                "text": "380 New York St Redlands CA 92373",
                                "sourceCountry": "US",
                            }
                        },
                        {
                            "geometry": {
                                "rings": [
                                    [
                                        [-117.185412, 34.063170],
                                        [-122.81, 37.81],
                                        [-117.200570, 34.057196],
                                        [-117.185412, 34.063170],
                                    ]
                                ],
                                "spatialReference": {"wkid": 4326},
                            },
                            "attributes": {
                                "id": "3",
                                "name": "optional polygon area name",
                            },
                        },
                    ]
        enrich_res = enrich(raw_json, gis=usa_agol._gis)
        assert isinstance(enrich_res, pd.DataFrame)


@skip_if_no_agol
def test_single_address_string_agol(usa_agol, usa_agol_enrich_vars):

    with does_not_raise():
        enrich_res = usa_agol.enrich('111 Market St NW, Olympia, WA 98502', enrich_variables=usa_agol_enrich_vars)
        assert isinstance(enrich_res, pd.DataFrame)


@skip_if_no_agol
def test_enrich_sedf_from_agol_layer_global_defaults(usa_agol):

    from arcgis.geoenrichment import enrich
    from arcgis.gis import GIS

    with does_not_raise():
        lyr = GIS().content.get('07bd93b6aba249b2b5972f7e2b9117a9').layers[0]
        df = lyr.query(as_df=True)
        enrich_res = enrich(df, gis=usa_agol._gis)
        assert isinstance(enrich_res, pd.DataFrame)
        assert _is_geoenabled(enrich_res)

@skip_if_no_agol
def test_name_areas_as_inputs(use_agol):
    from arcgis.geoenrichment import enrich
    
    with does_not_raise():
        # One named area
        usa = Country.get('US')
        redlands = usa.subgeographies.states['California'].zip5['92373']
        enriched = enrich([redlands])
        assert isinstance(enriched, pd.DataFrame)
        assert _is_geoenabled(enriched)

        # A dictionary of named areas
        ca_counties = usa.subgeographies.states['California'].counties
        counties_df = enrich(study_areas=ca_counties)
        assert isinstance(counties_df, pd.DataFrame)
        assert _is_geoenabled(counties_df)
