from arcgis.gis import GIS
from arcgis.geoenrichment import Country
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


def get_san_bernardino_test(src: GIS, expectation: object):
    with expectation:
        cntry = Country('usa', gis=src)
        res = cntry.subgeographies.states['California'].counties['San_Bernardino_County']
        assert isinstance(res, pd.DataFrame)


@skip_if_no_agol
def test_get_san_bernardino_agol(gis_agol):
    get_san_bernardino_test(gis_agol, does_not_raise())
