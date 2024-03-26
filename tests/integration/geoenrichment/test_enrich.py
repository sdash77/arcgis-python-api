import unittest
from typing import Union, Iterable

import numpy as np

from arcgis.features import FeatureSet
from arcgis.features.geo import _is_geoenabled
from arcgis.geometry import Point
from arcgis.geoenrichment import Country
from arcgis.geoenrichment._business_analyst._utils import pep8ify
import pandas as pd
from utils.decorators import integration_test

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
    abbreviated_test
)


# root tests
def enrich_check(
    enrich_src: Country,
    geom: Union[pd.DataFrame, pd.Series, Iterable],
    enrich_vars: Union[pd.DataFrame, list],
    expectation: object,
    std_geo_lvl: Union[str, int] = None,
    std_geo_id_col: str = None,
    prx_typ: str = None,
    prx_val: Union[int, float] = None,
    prx_mtrc: str = None,
    output_spatial_reference: int = 4326,
    sanitize_columns: bool = True,
) -> None:
    with expectation:

        enrich_res = enrich_src.enrich(
            geom,
            enrich_vars,
            standard_geography_level=std_geo_lvl,
            standard_geography_id_column=std_geo_id_col,
            proximity_type=prx_typ,
            proximity_value=prx_val,
            proximity_metric=prx_mtrc,
            output_spatial_reference=output_spatial_reference,
            sanitize_columns=sanitize_columns,
        )

        assert isinstance(enrich_res, pd.DataFrame)

        assert enrich_res.spatial.validate()

        if isinstance(enrich_vars, list):
            enrich_vars = enrich_src._ba_cntry.get_enrich_variables_from_iterable(
                enrich_vars
            )
        if sanitize_columns:
            enrich_var_cols = [pep8ify(val) for val in enrich_vars["name"]]
        else:
            enrich_var_cols = [val for val in enrich_vars["name"]]
        enrich_res_cols = list(enrich_res.columns)
        assert all([(enrich_col in enrich_res_cols) for enrich_col in enrich_var_cols])

        if enrich_src == "local":
            # if input is data frame (except for std geo), also check that all source fields are still there
            if isinstance(geom, pd.DataFrame) and not std_geo_lvl:
                input_columns = [
                    c.lower() for c in geom.columns if c != geom.spatial.name
                ]
                assert all(
                    [(input_col in enrich_res_cols) for input_col in input_columns]
                ), ("Missing some of the " + " columns of input data frame")

                # check if input and output data frames have the same length
                assert len(geom) == len(enrich_res), (
                    f"Input and output are expected to be of the same length."
                    f" Input length: {len(geom)}, output length: {len(enrich_res)}"
                )

        if output_spatial_reference:
            assert enrich_res.spatial.sr.wkid == output_spatial_reference


def enrich_feature_set_check(
    enrich_src: Country,
    geom: Union[pd.DataFrame, FeatureSet],
    enrich_vars: Union[pd.DataFrame, list],
    expectation: object,
    std_geo_lvl: Union[str, int] = None,
    std_geo_id_col: str = None,
    prx_typ: str = None,
    prx_val: Union[int, float] = None,
    prx_mtrc: str = None,
) -> None:
    with expectation:

        if isinstance(geom, FeatureSet):
            geom = geom.spatial.to_featurset()

        enrich_res = enrich_src.enrich(
            geom,
            enrich_vars,
            standard_geography_level=std_geo_lvl,
            standard_geography_id_column=std_geo_id_col,
            proximity_type=prx_typ,
            proximity_value=prx_val,
            proximity_metric=prx_mtrc,
        )

        assert isinstance(enrich_res, pd.DataFrame)

        assert enrich_res.spatial.validate()

        if isinstance(enrich_vars, list):
            enrich_vars = enrich_src._ba_cntry.get_enrich_variables_from_iterable(
                enrich_vars
            )
        enrich_var_cols = [pep8ify(val) for val in enrich_vars["name"]]
        enrich_res_cols = list(enrich_res.columns)
        assert all([[enrich_col in enrich_res_cols] for enrich_col in enrich_var_cols])


def enrich_do_not_return_geom_check(
    enrich_src: Country,
    geom_df: pd.DataFrame,
    enrich_vars: Union[pd.DataFrame, list],
    expectation: object,
    std_geo_lvl: Union[str, int] = None,
    std_geo_id_col: str = None,
) -> None:
    with expectation:

        enrich_res = enrich_src.enrich(
            geom_df,
            enrich_vars,
            standard_geography_level=std_geo_lvl,
            standard_geography_id_column=std_geo_id_col,
            return_geometry=False,
        )

        assert isinstance(enrich_res, pd.DataFrame)

        assert "SHAPE" not in list(enrich_res.columns)

        assert enrich_res.spatial.validate() is False

        if isinstance(enrich_vars, list):
            enrich_vars = enrich_src._ba_cntry.get_enrich_variables_from_iterable(
                enrich_vars
            )
        enrich_var_cols = [pep8ify(val) for val in enrich_vars["enrich_field_name"]]
        enrich_res_cols = list(enrich_res.columns)
        assert all([[enrich_col in enrich_res_cols] for enrich_col in enrich_var_cols])


def enrich_json_input_check(
    enrich_src: Country, enrich_vars: pd.DataFrame, expectation: object
) -> None:

    with expectation:

        geom = [
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
                "attributes": {"id": "1", "name": "optional polygon area name"},
            }
        ]

        enrich_res = enrich_src.enrich(geom, enrich_vars)

        if isinstance(enrich_vars, list):
            enrich_vars = enrich_src._ba_cntry.get_enrich_variables_from_iterable(
                enrich_vars
            )
        assert isinstance(enrich_res, pd.DataFrame)
        enrich_var_cols = [pep8ify(val) for val in enrich_vars["enrich_field_name"]]
        enrich_res_cols = list(enrich_res.columns)
        assert all([[enrich_col in enrich_res_cols] for enrich_col in enrich_var_cols])


def enrich_geometry_list_check(
    enrich_src: Country,
    enrich_vars: Union[pd.DataFrame, list],
    expectation: object = does_not_raise(),
) -> None:
    with expectation:
        geom_lst = [
            Point({"x": -122.435, "y": 37.785, "spatialReference": {"wkid": 4326}}),
            Point({"x": -122.433, "y": 37.734, "spatialReference": {"wkid": 4326}}),
        ]

        enrich_res = enrich_src.enrich(geom_lst, enrich_variables=enrich_vars)

        assert isinstance(enrich_res, pd.DataFrame)

        if isinstance(enrich_vars, list):
            enrich_vars = enrich_src._ba_cntry.get_enrich_variables_from_iterable(
                enrich_vars
            )
        enrich_var_cols = [pep8ify(val) for val in enrich_vars["enrich_field_name"]]
        enrich_res_cols = list(enrich_res.columns)
        assert all([[enrich_col in enrich_res_cols] for enrich_col in enrich_var_cols])


@integration_test
class TestEnrichLocal(unittest.TestCase):
    def setUp(self):
        self.usa_agol_inst = usa_agol()
        self.usa_agol_enrich_vars_inst = usa_agol_enrich_vars()
        self.polygon_df_inst = polygon_df()
        self.line_df_inst = line_df()
        self.point_df_inst = point_df()
        self.stdgeo_srs_inst = stdgeo_srs()

    # local
    @skip_if_no_local
    def test_enrich_usa_poly_df_local(self):
        usa_local_inst = usa_local()
        usa_local_enrich_vars_inst = usa_local_enrich_vars()

        df_with_objectid = self.polygon_df_inst.copy()
        df_with_objectid["OBJECTID"] = np.arange(1, len(df_with_objectid) + 1)
        df_with_objectid.spatial.set_geometry("SHAPE")

        enrich_check(
            usa_local_inst,
            df_with_objectid,
            usa_local_enrich_vars_inst,
            does_not_raise(),
        )

    @skip_if_no_local
    def test_enrich_usa_poly_project_local(self):
        usa_local_inst = usa_local()
        usa_local_enrich_vars_inst = usa_local_enrich_vars()
        enrich_check(
            usa_local_inst,
            self.polygon_df_inst,
            usa_local_enrich_vars_inst,
            does_not_raise(),
            output_spatial_reference=4269,
        )

    @skip_if_no_local
    def test_enrich_usa_line_implicit_local(self):
        usa_local_inst = usa_local()
        usa_local_enrich_vars_inst = usa_local_enrich_vars()
        enrich_check(
            usa_local_inst,
            self.line_df_inst,
            usa_local_enrich_vars_inst,
            does_not_raise(),
        )

    @skip_if_no_local
    def test_enrich_usa_line_explicit_local(self):
        usa_local_inst = usa_local()
        usa_local_enrich_vars_inst = usa_local_enrich_vars()
        enrich_check(
            usa_local_inst,
            self.line_df_inst,
            usa_local_enrich_vars_inst,
            self.assertRaises(AssertionError),
            prx_typ="driving_time",
        )

    @skip_if_no_local
    def test_enrich_usa_point_straightline_implicit_local(self):
        usa_local_inst = usa_local()
        usa_local_enrich_vars_inst = usa_local_enrich_vars()
        enrich_check(
            usa_local_inst,
            self.point_df_inst,
            usa_local_enrich_vars_inst,
            does_not_raise(),
        )

    @skip_if_no_local
    def test_enrich_usa_point_straightline_explicit_local(self):
        usa_local_inst = usa_local()
        usa_local_enrich_vars_inst = usa_local_enrich_vars()
        enrich_check(
            usa_local_inst,
            self.point_df_inst,
            usa_local_enrich_vars_inst,
            does_not_raise(),
            prx_typ="straight_line",
        )

    @skip_if_no_local
    def test_enrich_usa_point_drivedistance_local(self):
        usa_local_inst = usa_local()
        usa_local_enrich_vars_inst = usa_local_enrich_vars()
        enrich_check(
            usa_local_inst,
            self.point_df_inst,
            usa_local_enrich_vars_inst,
            does_not_raise(),
            prx_typ="driving_distance",
            prx_val=10,
            prx_mtrc="miles",
        )

    @skip_if_no_local
    def test_enrich_usa_point_drivetime_local(self):
        usa_local_inst = usa_local()
        usa_local_enrich_vars_inst = usa_local_enrich_vars()
        enrich_check(
            usa_local_inst,
            self.point_df_inst,
            usa_local_enrich_vars_inst,
            does_not_raise(),
            prx_typ="driving_time",
            prx_val=12,
            prx_mtrc="minutes",
        )

    @skip_if_no_local
    def test_enrich_usa_no_return_geomery_local(self):
        usa_local_inst = usa_local()
        usa_local_enrich_vars_inst = usa_local_enrich_vars()
        enrich_do_not_return_geom_check(
            usa_local_inst,
            self.polygon_df_inst,
            usa_local_enrich_vars_inst,
            does_not_raise(),
        )

    @skip_if_no_local
    def test_enrich_usa_stdgeo_srs_local(self):
        usa_local_inst = usa_local()
        usa_local_enrich_vars_inst = usa_local_enrich_vars()
        enrich_check(
            usa_local_inst,
            self.stdgeo_srs_inst.iloc[:10],
            usa_local_enrich_vars_inst,
            does_not_raise(),
            std_geo_lvl="block_groups",
        )

    @skip_if_no_local
    def test_enrich_usa_stdgeo_srs_no_return_geom_local(self):
        usa_local_inst = usa_local()
        usa_local_enrich_vars_inst = usa_local_enrich_vars()
        enrich_do_not_return_geom_check(
            usa_local_inst,
            self.stdgeo_srs_inst,
            usa_local_enrich_vars_inst,
            does_not_raise(),
            std_geo_lvl="block_groups",
        )

    @skip_if_no_local
    def test_enrich_usa_stdgeo_df_local(self):
        usa_local_inst = usa_local()
        usa_local_enrich_vars_inst = usa_local_enrich_vars()
        polygon_df_inst_dropped = self.polygon_df_inst.drop(columns="SHAPE")
        enrich_check(
            usa_local_inst,
            polygon_df_inst_dropped,
            usa_local_enrich_vars_inst,
            does_not_raise(),
            std_geo_lvl="block_groups",
            std_geo_id_col="ID",
        )

    @skip_if_no_local
    def test_enrich_usa_variable_name_list_local(self):
        usa_local_inst = usa_local()
        enrich_check(
            usa_local_inst,
            self.polygon_df_inst,
            ["populationtotals.TOTPOP_CY", "AtRisk.TOTPOP_CY"],
            does_not_raise(),
        )

    @skip_if_no_local
    def test_enrich_local_save_original_column_names(self):
        usa_local_inst = usa_local()
        enrich_check(
            usa_local_inst,
            self.polygon_df_inst,
            ["populationtotals.TOTPOP_CY", "AtRisk.TOTPOP_CY"],
            does_not_raise(),
            sanitize_columns=False,
        )

    @skip_if_no_local
    def test_enrich_usa_after_can_variable_name_list_local(self):
        import arcpy

        arcpy.env.baDataSource = "LOCAL;;CAN_ESRI_2021"
        usa_local_inst = usa_local()
        enrich_check(
            usa_local_inst,
            self.polygon_df_inst,
            ["populationtotals.TOTPOP_CY", "AtRisk.TOTPOP_CY"],
            does_not_raise(),
        )

    @skip_if_no_local
    def test_enrich_json_local(self):
        usa_local_inst = usa_local()
        usa_local_enrich_vars_inst = usa_local_enrich_vars()
        enrich_json_input_check(
            usa_local_inst, usa_local_enrich_vars_inst, self.assertRaises(ValueError)
        )

    from unittest import mock

    @skip_if_no_local
    @mock.patch("arcpy.GetInstallInfo", mock.MagicMock(return_value={"Version": "2.9"}))
    def test_pro_at_least_version29(self):
        from arcgis.geoenrichment._business_analyst._utils import pro_at_least_version

        self.assertTrue(pro_at_least_version("2.9"))
        self.assertFalse(pro_at_least_version("3.0"))
        self.assertFalse(pro_at_least_version("3.0.1"))
        self.assertTrue(pro_at_least_version("2.8.3"))

    @skip_if_no_local
    @mock.patch(
        "arcpy.GetInstallInfo", mock.MagicMock(return_value={"Version": "3.1.4"})
    )
    def test_pro_at_least_version314(self):
        from arcgis.geoenrichment._business_analyst._utils import pro_at_least_version

        self.assertTrue(pro_at_least_version("3.0"))
        self.assertFalse(pro_at_least_version("3.9"))
        self.assertFalse(pro_at_least_version("3.1.5"))
        self.assertTrue(pro_at_least_version("3.0.3"))


@integration_test
class TestEnrichOnline(unittest.TestCase):
    def setUp(self):
        self.usa_agol_inst = usa_agol()
        self.usa_agol_enrich_vars_inst = usa_agol_enrich_vars()
        self.polygon_df_inst = polygon_df()
        self.line_df_inst = line_df()
        self.point_df_inst = point_df()
        self.stdgeo_srs_inst = stdgeo_srs()

        self.stdgeo_srs_inst_orig = self.stdgeo_srs_inst
        self.point_df_inst_orig = self.point_df_inst
        self.line_df_inst_orig = self.line_df_inst
        self.polygon_df_inst_orig = self.polygon_df_inst

        if abbreviated_test:
            self.usa_agol_enrich_vars_inst = self.usa_agol_enrich_vars_inst.head(10)

            shape_column = self.polygon_df_inst.spatial.name
            self.polygon_df_inst = self.polygon_df_inst.head(20)
            self.polygon_df_inst.spatial.set_geometry(shape_column)

            shape_column = self.line_df_inst.spatial.name
            self.line_df_inst = self.line_df_inst.head(10)
            self.line_df_inst.spatial.set_geometry(shape_column)

            shape_column = self.point_df_inst.spatial.name
            self.point_df_inst = self.point_df_inst.head(10)
            self.point_df_inst.spatial.set_geometry(shape_column)

            self.stdgeo_srs_inst = self.stdgeo_srs_inst.head(10)

    # ArcGIS Online
    @skip_if_no_agol
    def test_enrich_usa_stdgeo_srs_usa_agol(self):
        enrich_check(
            self.usa_agol_inst,
            self.stdgeo_srs_inst,
            self.usa_agol_enrich_vars_inst,
            does_not_raise(),
            std_geo_lvl="block_groups",
        )

    @skip_if_no_agol
    def test_enrich_usa_stdgeo_srs_no_return_geom_agol(self):
        enrich_do_not_return_geom_check(
            self.usa_agol_inst,
            self.stdgeo_srs_inst,
            self.usa_agol_enrich_vars_inst,
            does_not_raise(),
            std_geo_lvl="block_groups",
        )

    @skip_if_no_agol
    def test_enrich_usa_stdgeo_df_agol(self):
        polygon_df_inst_dropped = self.polygon_df_inst.drop(columns="SHAPE")
        enrich_check(
            self.usa_agol_inst,
            polygon_df_inst_dropped,
            self.usa_agol_enrich_vars_inst,
            does_not_raise(),
            std_geo_lvl="block_groups",
            std_geo_id_col="ID",
        )

    @skip_if_no_agol
    def test_enrich_usa_poly_singlebatch_agol(self):
        polygon_df_inst_sample = self.polygon_df_inst_orig.iloc[:45]
        polygon_df_inst_sample.spatial.set_geometry("SHAPE")
        enrich_check(
            self.usa_agol_inst,
            polygon_df_inst_sample,
            self.usa_agol_enrich_vars_inst,
            does_not_raise(),
        )

    @skip_if_no_agol
    def test_enrich_usa_poly_agol(self):
        enrich_check(
            self.usa_agol_inst,
            self.polygon_df_inst,
            self.usa_agol_enrich_vars_inst,
            does_not_raise(),
        )

    @skip_if_no_agol
    def test_enrich_feature_set_usa_poly_agol(self):
        enrich_feature_set_check(
            self.usa_agol_inst,
            self.polygon_df_inst,
            self.usa_agol_enrich_vars_inst,
            does_not_raise(),
        )

    @skip_if_no_agol
    def test_enrich_usa_line_agol(self):
        enrich_check(
            self.usa_agol_inst,
            self.line_df_inst,
            self.usa_agol_enrich_vars_inst,
            does_not_raise(),
        )

    @skip_if_no_agol
    def test_enrich_usa_point_drivedistance_agol(self):
        enrich_check(
            self.usa_agol_inst,
            self.point_df_inst,
            self.usa_agol_enrich_vars_inst,
            does_not_raise(),
            prx_typ="drive_distance",
            prx_val=10,
            prx_mtrc="miles",
        )

    @skip_if_no_agol
    def test_enrich_usa_point_drivetime_agol(self):
        enrich_check(
            self.usa_agol_inst,
            self.point_df_inst,
            self.usa_agol_enrich_vars_inst,
            does_not_raise(),
            prx_typ="drive_time",
            prx_val=12,
            prx_mtrc="minutes",
        )

    @skip_if_no_agol
    def test_enrich_json_agol(self):
        enrich_json_input_check(
            self.usa_agol_inst, self.usa_agol_enrich_vars_inst, does_not_raise()
        )

    @skip_if_no_agol
    def test_enrich_usa_variable_name_list_agol(self):
        enrich_check(
            self.usa_agol_inst,
            self.polygon_df_inst,
            ["populationtotals.TOTPOP_CY", "AtRisk.TOTPOP_CY"],
            does_not_raise(),
        )

    @skip_if_no_agol
    def test_enrich_geometry_list_agol(self):
        enrich_geometry_list_check(
            self.usa_agol_inst, self.usa_agol_enrich_vars_inst, does_not_raise()
        )

    @skip_if_no_agol
    def test_enrich_buffer_multiple_addresses_agol(self):

        with does_not_raise():
            address_lst = [
                "380 New York St, Redlands CA, 92373",
                "111 Market St, Olympia WA, 98501",
            ]
            enrich_res = self.usa_agol_inst.enrich(
                address_lst, enrich_variables=self.usa_agol_enrich_vars_inst
            )
            assert isinstance(enrich_res, pd.DataFrame)

    @skip_if_no_agol
    def test_enrich_large_json_no_enrich_vars(self):

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
            enrich_res = enrich(raw_json, gis=self.usa_agol_inst._gis)
            assert isinstance(enrich_res, pd.DataFrame)

    @skip_if_no_agol
    def test_enrich_mix_point_poly(self):

        from arcgis.geoenrichment import enrich

        with does_not_raise():
            raw_json = [
                {
                    "geometry": {"x": -122.435, "y": 37.785},
                    "attributes": {"id": "1"},
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
            enrich_res = enrich(raw_json, gis=self.usa_agol_inst._gis)
            assert isinstance(enrich_res, pd.DataFrame)

    @skip_if_no_agol
    def test_single_address_string_agol(self):

        with does_not_raise():
            enrich_res = self.usa_agol_inst.enrich(
                "111 Market St NW, Olympia, WA 98502",
                enrich_variables=self.usa_agol_enrich_vars_inst,
            )
            assert isinstance(enrich_res, pd.DataFrame)

    @skip_if_no_agol
    def test_enrich_sedf_from_agol_layer_global_defaults(self):

        from arcgis.geoenrichment import enrich
        from arcgis.gis import GIS

        with does_not_raise():
            lyr = GIS().content.get("07bd93b6aba249b2b5972f7e2b9117a9").layers[0]
            df = lyr.query(as_df=True)
            enrich_res = enrich(df, gis=self.usa_agol_inst._gis)
            assert isinstance(enrich_res, pd.DataFrame)
            assert _is_geoenabled(enrich_res)

    @skip_if_no_agol
    def test_name_areas_as_inputs(self):
        from arcgis.geoenrichment import enrich

        with does_not_raise():
            # One named area
            usa = Country.get("US")
            redlands = usa.subgeographies.states["California"].zip5["92373"]
            enriched = enrich([redlands], gis=self.usa_agol_inst._gis)
            assert isinstance(enriched, pd.DataFrame)
            assert _is_geoenabled(enriched)

            # A dictionary of named areas
            ca_counties = usa.subgeographies.states["California"].counties
            counties_df = enrich(study_areas=ca_counties, gis=self.usa_agol_inst._gis)
            assert isinstance(counties_df, pd.DataFrame)
            assert _is_geoenabled(counties_df)

    @skip_if_no_agol
    def test_enrich_buffer_study_area_driving_time_ge_format(self):
        from arcgis.geoenrichment import enrich, BufferStudyArea

        with does_not_raise():
            buffered = BufferStudyArea(
                area="380 New York St Redlands CA 92373",
                radii=[3],
                units="Miles",
                overlap=False,
                travel_mode="driving",
            )
            buffer_df = enrich(study_areas=[buffered], gis=self.usa_agol_inst._gis)
            assert isinstance(buffer_df, pd.DataFrame)
            assert _is_geoenabled(buffer_df)
            assert buffer_df.iloc[0]["buffer_units_alias"] == "Drive Distance Miles"

    @skip_if_no_agol
    def test_enrich_buffer_study_area_walking_time_ge_format(self):
        from arcgis.geoenrichment import enrich, BufferStudyArea

        with does_not_raise():
            buffered = BufferStudyArea(
                area="380 New York St Redlands CA 92373",
                radii=[30],
                units="Minutes",
                overlap=False,
                travel_mode="walking",
            )
            buffer_df = enrich(study_areas=[buffered], gis=self.usa_agol_inst._gis)
            assert isinstance(buffer_df, pd.DataFrame)
            assert _is_geoenabled(buffer_df)
            assert buffer_df.iloc[0]["buffer_units_alias"] == "Walk Time Minutes"

    @skip_if_no_agol
    def test_enrich_buffer_study_area_trucking_distance_ge_format(self):
        from arcgis.geoenrichment import enrich, BufferStudyArea

        with does_not_raise():
            buffered = BufferStudyArea(
                area="380 New York St Redlands CA 92373",
                radii=[3],
                units="Miles",
                overlap=False,
                travel_mode="trucking",
            )
            buffer_df = enrich(study_areas=[buffered], gis=self.usa_agol_inst._gis)
            assert isinstance(buffer_df, pd.DataFrame)
            assert _is_geoenabled(buffer_df)
            assert buffer_df.iloc[0]["buffer_units_alias"] == "Truck Distance Miles"

    @skip_if_no_agol
    def test_enrich_buffer_study_area_walking_time(self):
        from arcgis.geoenrichment import enrich, BufferStudyArea

        with does_not_raise():
            buffered = BufferStudyArea(
                area="380 New York St Redlands CA 92373",
                radii=[30],
                units="Minutes",
                overlap=False,
                travel_mode="walking_time",
            )
            buffer_df = enrich(study_areas=[buffered], gis=self.usa_agol_inst._gis)
            assert isinstance(buffer_df, pd.DataFrame)
            assert _is_geoenabled(buffer_df)
            assert buffer_df.iloc[0]["buffer_units_alias"] == "Walk Time Minutes"

    @skip_if_no_agol
    def test_travel_modes(self):
        with does_not_raise():
            # One named area
            usa = Country.get("US")
            travel_modes = usa.travel_modes

            assert isinstance(travel_modes, pd.DataFrame)
    
    @skip_if_no_agol
    def test_analysis_variables(self):
        from arcgis.geoenrichment import enrich, BufferStudyArea

        with does_not_raise():
            buffer_area = BufferStudyArea(area=Point({"x":-117.146007, "y":34.079086, "spatialReference": {"wkid":4326}}))
            assert buffer_area

            enriched_areas = enrich(study_areas=[buffer_area], analysis_variables=["KeyGlobalFacts.TOTPOP"])
            assert enriched_areas
            assert isinstance(enriched_areas, pd.DataFrame)
            assert _is_geoenabled(enriched_areas)

    @skip_if_no_agol
    def test_enrich_save_original_column_names(self):
        from arcgis.geoenrichment import enrich, BufferStudyArea

        with does_not_raise():
            buffered = BufferStudyArea(
                area="380 New York St Redlands CA 92373",
                radii=[3],
                units="Miles",
                overlap=False,
                travel_mode="driving",
            )
            enrich_res = enrich(study_areas=[buffered], gis=self.usa_agol_inst._gis, sanitize_columns=False)
            assert isinstance(enrich_res, pd.DataFrame)
            assert _is_geoenabled(enrich_res)
            enrich_res_cols = list(enrich_res.columns)
            sanitized_enrich_var_cols = [pep8ify(val) for val in enrich_res_cols if pep8ify(val) != val]
            assert all([(enrich_col not in enrich_res_cols) for enrich_col in sanitized_enrich_var_cols])


if __name__ == "__main__":

    unittest.main()
