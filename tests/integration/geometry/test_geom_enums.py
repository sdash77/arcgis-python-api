import unittest
import sys
from arcgis.gis import GIS
from arcgis.geometry import (
    areas_and_lengths,
    Geometry,
    functions,
    LengthUnits,
    AreaUnits,
)

PROFILES = ["your_online_profile", "your_enterprise_profile"]


class TestGeometryServiceWithEnums(unittest.TestCase):
    def test_method_with_enum(self):
        for profile in PROFILES:

            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            d = {
                "rings": [
                    [
                        [-97.06138, 32.837],
                        [-97.06133, 32.836],
                        [-97.06124, 32.834],
                        [-97.06127, 32.832],
                        [-97.06138, 32.837],
                    ],
                    [
                        [-97.06326, 32.759],
                        [-97.06298, 32.755],
                        [-97.06153, 32.749],
                        [-97.06326, 32.759],
                    ],
                ],
                "spatialReference": {"wkid": 4326},
            }
            geom = Geometry(d)

            res = areas_and_lengths(
                polygons=[geom],
                length_unit=LengthUnits.FOOT,
                area_unit=AreaUnits.ACRES,
                calculation_type="preserveShape",
            )
            assert "areas" in res
            assert "lengths" in res

    def test_area_units(self):
        assert AreaUnits.SQUAREINCHES.value == {"areaUnit": "esriSquareInches"}

    def test_length_units(self):
        assert LengthUnits.BRITISH1936FOOT.value == 9095


if __name__ == "__main__":
    unittest.main()
