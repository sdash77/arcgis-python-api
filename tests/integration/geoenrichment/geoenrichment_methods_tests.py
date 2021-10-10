import pandas as pd
from typing import Union

from arcgis.geoenrichment import (
    Country,
    get_countries,
    create_report,
    enrich,
    standard_geography_query,
    service_limits,
)
from arcgis.gis import GIS

from .geoenrich_data import (
    address_list_str,
    address_list_json,
    key_enrich_list_web,
    block_group_df,
    block_group_points_df,
)


def get_countries_test(gis: GIS = None) -> None:
    cntrs = get_countries(gis)
    assert cntrs


def enrich_iterable_str_addresses_test(gis: GIS = None) -> None:
    er = enrich(address_list_str, analysis_variables=key_enrich_list_web, gis=gis)
    assert isinstance(er, pd.DataFrame)
    assert er.spatial.validate()


# def enrich_iterable_str_points_of_interest_test() -> None:
#     assert False
#
#
# def enrich_iterable_str_place_names() -> None:
#     assert False


def enrich_iterable_dict_addresses_test(gis: GIS = None) -> None:
    er = enrich(address_list_json, analysis_variables=key_enrich_list_web, gis=gis)
    assert isinstance(er, pd.DataFrame)
    assert er.spatial.validate()


def enrich_iterable_geometry_test(gis: GIS = None) -> None:
    geom_lst = list(block_group_df.SHAPE)
    er = enrich(geom_lst, analysis_variables=key_enrich_list_web, gis=gis)
    assert isinstance(er, pd.DataFrame)
    assert er.spatial.validate()


def enrich_iterable_buffer_study_areas_test(gis: GIS = None) -> None:
    geom_lst = list(block_group_points_df.SHAPE)
    er = enrich(geom_lst, analysis_variables=key_enrich_list_web, gis=gis)
    assert isinstance(er, pd.DataFrame)
    assert er.spatial.validate()


def enrich_sedf_test(gis: GIS = None) -> None:
    er = enrich(block_group_df, analysis_variables=key_enrich_list_web, gis=gis)
    assert isinstance(er, pd.DataFrame)
    assert er.spatial.validate()


def get_named_areas_test(gis: GIS = None) -> None:
    cntry = Country.get("usa", gis=gis)
    zip90018 = cntry.subgeographies.states["California"].zip5["90018"]
    assert zip90018


# def enrich_iterable_named_areas_test() -> None:
#     assert False
#
#
# def standard_geography_query_seattle_test() -> None:
#     assert False
#
#
# def standard_geography_query_seattle_zip_test():
#     assert False
#
#
# def standard_geography_query_zip_list():
#     assert False
