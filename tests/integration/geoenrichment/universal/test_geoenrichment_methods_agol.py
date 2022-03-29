from ..geoenrichment_methods_tests import *
from ..geoenrich_data import gis_agol


def test_get_countries_agol():
    get_countries(gis_agol)


def test_enrich_iterable_dict_address_agol():
    enrich_iterable_dict_addresses_test(gis_agol)


def test_enrich_iterable_geometry_agol():
    enrich_iterable_geometry_test(gis_agol)


def test_enrich_sedf_agol():
    enrich_sedf_test(gis_agol)


def test_enrich_iterable_buffer_study_areas_agol():
    enrich_iterable_buffer_study_areas_test(gis_agol)


def test_get_named_areas_implicit():
    get_named_areas_test()


def test_get_named_areas_agol_explicit():
    get_named_areas_test(gis_agol)
