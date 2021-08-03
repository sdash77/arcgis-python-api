import pytest

from ..geoenrichment_country_tests import *

@pytest.fixture
def usa():
    return Country.get('USA', gis='local')


def test_usa_local() -> None:
    usa_test('local')


def test_get_usa_local() -> None:
    get_usa_test('local')


def test_test_get_can_local() -> None:
    get_can_test('local')


def test_get_usa_2019_local() -> None:
    get_usa_2019_test('local')


def test_dataset_local(usa) -> None:
    with pytest.raises(NotImplementedError):
        dataset_test(usa)


def test_data_collections_local(usa) -> None:
    data_collections_test(usa)


def test_enrich_variables(usa) -> None:
    enrich_variables_test(usa)


def test_geometry_local(usa) -> None:
    with pytest.raises(NotImplementedError):
        geometry_test(usa)


def test_levels_local(usa) -> None:
    with pytest.raises(NotImplementedError):
        levels_test(usa)


def test_reports_local(usa) -> None:
    with pytest.raises(NotImplementedError):
        reports_test(usa)


# def test_search_cbsa_chicago_local(usa) -> None:
#     with pytest.raises(NotImplementedError):
#         search_cbsa_chicago(usa)
#
#
# def test_subgeographies_local(usa) -> None:
#     with pytest.raises(NotImplementedError):
#         subgeographies_test(usa)
