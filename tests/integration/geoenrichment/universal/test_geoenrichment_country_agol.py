from arcgis.gis import GIS
import pytest

from ..geoenrichment_country_tests import *
from ..geoenrich_data import gis_agol

@pytest.fixture
def usa():
    return Country.get('USA', gis=gis_agol)


def test_usa_agol() -> None:
    usa_test(gis_agol)


def test_get_usa_agol() -> None:
    get_usa_test(gis_agol)


def test_test_get_can_agol() -> None:
    get_can_test(gis_agol)


def test_get_usa_2019_agol() -> None:
    with pytest.warns(Warning):
        get_usa_2019_test(gis_agol)


def test_dataset_agol(usa) -> None:
    dataset_test(usa)


def test_enrich_variables_agol(usa) -> None:
    enrich_variables_test(usa)


def test_data_collections_agol(usa) -> None:
    data_collections_test(usa)


def test_geometry_agol(usa) -> None:
    geometry_test(usa)


def test_levels_agol(usa) -> None:
    levels_test(usa)


def test_reports_agol(usa) -> None:
    reports_test(usa)


def test_search_cbsa_chicago_agol(usa) -> None:
    search_cbsa_chicago(usa)


def test_subgeographies_agol(usa) -> None:
    subgeographies_test(usa)
