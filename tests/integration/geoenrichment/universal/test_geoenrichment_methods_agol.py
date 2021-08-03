from ..geoenrichment_methods_tests import *
from ..geoenrich_data import gis


def test_get_countries_agol():
    get_countries(gis)


def test_enrich_iterable_str_address_agol():
    enrich_iterable_str_addresses_test()


def test_enrich_interable_str_points_of_interest_agol():
    enrich_iterable_str_points_of_interest_test()


def test_enrich_iterable_str_place_names_agol():
    enrich_iterable_str_place_names()


def test_enrich_iterable_dict_address_agol():
    enrich_iterable_dict_addresses_test()


def test_enrich_iterable_geometry_agol():
    enrich_iterable_geometry_test()


def test_enrich_sedf_agol():
    enrich_sedf_test()


def test_enrich_iterable_buffer_study_areas_agol():
    enrich_iterable_buffer_study_areas_test()


def test_enrich_iterable_named_areas_agol():
    enrich_iterable_named_areas_test()


def test_standard_geography_query_seattle_agol():
    standard_geography_query_seattle_test()


def test_standard_geography_query_seattle_zip_agol():
    standard_geography_query_seattle_zip_test()
