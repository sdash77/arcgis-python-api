from arcgis.gis import GIS
from arcgis.geoenrichment import get_countries, Country
import pandas as pd

from .configtest import (
    does_not_raise,
    skip_if_no_local,
    skip_if_no_agol,
    gis_pro,
    gis_agol,
    usa_local,
    usa_agol
)


# root tests
def get_countries_test(src: GIS, expectation: object) -> None:
    with expectation:
        res = get_countries(src)
        assert isinstance(res, pd.DataFrame)
        assert len(res.index)


def get_enrich_variables_test(cntry: Country, expectation: object) -> None:
    with expectation:
        res = cntry.enrich_variables
        assert isinstance(res, pd.DataFrame)
        assert len(res.index)


def get_country_levels_test(cntry: Country, expectation: object) -> None:
    with expectation:
        res = cntry.levels
        assert isinstance(res, pd.DataFrame)
        assert len(res.index)


# local
@skip_if_no_local
def test_get_countries_local(gis_pro):
    get_countries_test(gis_pro, does_not_raise())


@skip_if_no_local
def test_get_enrich_variables_local(usa_local):
    get_enrich_variables_test(usa_local, does_not_raise())


@skip_if_no_local
def test_get_country_levels_local(usa_local):
    get_country_levels_test(usa_local, does_not_raise())


# ArcGIS Online
@skip_if_no_agol
def test_get_countries_agol(gis_agol):
    get_countries_test(gis_agol, does_not_raise())


@skip_if_no_agol
def test_get_enrich_variables_agol(usa_agol):
    get_enrich_variables_test(usa_agol, does_not_raise())


@skip_if_no_agol
def test_get_country_levels_agol(usa_agol):
    get_country_levels_test(usa_agol, does_not_raise())
