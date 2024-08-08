import unittest

from arcgis.gis import GIS
from arcgis.geoenrichment import get_countries, Country
import pandas as pd

from integration.geoenrichment.configtest import (
    does_not_raise,
    skip_if_no_local,
    skip_if_no_agol,
    gis_pro,
    gis_agol,
    usa_local,
    usa_agol,
)
from utils.decorators import integration_test


# root tests
def get_countries_check(src: GIS, expectation: object) -> None:
    with expectation:
        res = get_countries(src)
        assert isinstance(res, pd.DataFrame)
        assert len(res.index)


def get_enrich_variables_check(cntry: Country, expectation: object) -> None:
    with expectation:
        res = cntry.enrich_variables
        assert isinstance(res, pd.DataFrame)
        assert len(res.index)


def get_country_levels_check(cntry: Country, expectation: object) -> None:
    with expectation:
        res = cntry.levels
        assert isinstance(res, pd.DataFrame)
        assert len(res.index)


@integration_test
class TestIntrospection(unittest.TestCase):

    # local
    @skip_if_no_local
    def test_get_countries_local(self):
        gis_pro_inst = gis_pro()
        get_countries_check(gis_pro_inst, does_not_raise())

    @skip_if_no_local
    def test_get_enrich_variables_local(self):
        usa_local_inst = usa_local()
        get_enrich_variables_check(usa_local_inst, does_not_raise())

    @skip_if_no_local
    def test_get_country_levels_local(self):
        usa_local_inst = usa_local()
        get_country_levels_check(usa_local_inst, does_not_raise())

    # ArcGIS Online
    @skip_if_no_agol
    def test_get_countries_agol(self):
        gis_agol_inst = gis_agol()
        get_countries_check(gis_agol_inst, does_not_raise())

    @skip_if_no_agol
    def test_get_enrich_variables_agol(self):
        usa_agol_inst = usa_agol()
        get_enrich_variables_check(usa_agol_inst, does_not_raise())

    @skip_if_no_agol
    def test_get_country_levels_agol(self):
        usa_agol_inst = usa_agol()
        get_country_levels_check(usa_agol_inst, does_not_raise())


if __name__ == "__main__":

    unittest.main()
