import pandas as pd
import pytest

from arcgis.gis import GIS

from ..geoenrichment_methods_tests import *

gis = GIS('pro')


def test_get_countries_local():
    res = get_countries(gis)
    assert isinstance(res, list)


def test_get_countries_local_df():
    res = get_countries(gis, as_df=True)
    assert isinstance(res, pd.DataFrame)


def test_enrich_iterable_str_address_local():
    with pytest.raises(NotImplementedError):
        enrich_iterable_str_addresses_test()


# def test_enrich_iterable_str_points_of_interest_local():
#     enrich_iterable_str_points_of_interest_test()
#
#
# def test_enrich_iterable_str_place_names_local():
#     enrich_iterable_str_place_names()


def test_enrich_iterable_dict_address_local():
    with pytest.raises(NotImplementedError):
        enrich_iterable_dict_addresses_test()


def test_enrich_iterable_geometry_local():
    with pytest.raises(NotImplementedError):
        enrich_iterable_geometry_test()


def test_enrich_sedf_local():
    with pytest.raises(NotImplementedError):
        enrich_sedf_test()


def test_enrich_iterable_buffer_study_areas_local():
    with pytest.raises(NotImplementedError):
        enrich_iterable_buffer_study_areas_test()


# def test_enrich_iterable_named_areas_local():
#     enrich_iterable_named_areas_test()
#
#
# def test_standard_geography_query_seattle_local():
#     standard_geography_query_seattle_test()
#
#
# def test_standard_geography_query_seattle_zip_local():
#     standard_geography_query_seattle_zip_test()
