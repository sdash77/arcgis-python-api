import unittest

from arcgis.gis import GIS
from arcgis.geoenrichment import Country
from arcgis.geoenrichment.enrichment import NamedArea

from integration.geoenrichment.configtest import (
    does_not_raise,
    skip_if_no_agol,
    gis_agol,
)
from utils.decorators import integration_test


def get_san_bernardino_check(src: GIS, expectation: object):
    with expectation:
        cntry = Country('usa', gis=src)
        res = cntry.subgeographies.states['California'].counties['San_Bernardino_County']
        assert isinstance(res, NamedArea)


@integration_test
class TestQueryStdGeo(unittest.TestCase):

    def setUp(self):
        self.gis_agol_inst = gis_agol()

    @skip_if_no_agol
    def test_get_san_bernardino_agol(self):
        get_san_bernardino_check(self.gis_agol_inst, does_not_raise())


if __name__ == "__main__":

    unittest.main()
