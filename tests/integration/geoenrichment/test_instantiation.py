import unittest
from typing import Optional

from arcgis.gis import GIS
from arcgis.geoenrichment import Country

from integration.geoenrichment.configtest import (
    skip_if_no_agol,
    skip_if_no_local,
    does_not_raise,
    gis_pro,
    gis_agol,
    _agol_url as agol_url,
    _agol_user as agol_user,
    _agol_pass as agol_pass,
)
from utils.decorators import integration_test


def create_country_check(
    iso3: str, gis: GIS, expectation, year: Optional[int] = None
) -> None:
    with expectation:
        cntry = Country(iso3, gis=gis, year=year)
        assert isinstance(cntry, Country)


@integration_test
class TestInstantiation(unittest.TestCase):

    # including to ensure credentials correctly getting loaded from config and also ensure not lower level issues in GIS
    def test_create_gis(self):
        gis = GIS(agol_url, username=agol_user, password=agol_pass)
        assert isinstance(gis, GIS)
        assert gis._con._auth != "ANON"

    @skip_if_no_local
    def test_create_country_usa_local(self):
        gis_pro_inst = gis_pro()
        create_country_check("usa", gis=gis_pro_inst, expectation=does_not_raise())

    @skip_if_no_local
    def test_create_country_can_local(self):
        gis_pro_inst = gis_pro()
        create_country_check("can", gis=gis_pro_inst, expectation=does_not_raise())

    @skip_if_no_agol
    def test_create_country_usa_agol(self):
        gis_agol_inst = gis_agol()
        create_country_check("usa", gis=gis_agol_inst, expectation=does_not_raise())

    @skip_if_no_agol
    def test_create_country_can_agol(self):
        gis_agol_inst = gis_agol()
        create_country_check("can", gis=gis_agol_inst, expectation=does_not_raise())


if __name__ == "__main__":

    unittest.main()
