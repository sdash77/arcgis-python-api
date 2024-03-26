import os
import unittest

from arcgis.gis import GIS
from arcgis.features import FeatureLayer, FeatureSet
from utils.decorators import integration_test

# Needs to be on devext for now
gis = GIS(profile="your_online_profile", verify_cert=False)

# TODO: get better service with more features to be able to test better. Placeholder service
layer = FeatureLayer(
    "https://servicesdev.arcgis.com/5xC5Wrapp1gUAl2r/ArcGIS/rest/services/CUBE_WGS84_APIforPython/FeatureServer/0"
)


@integration_test
class TestQuery3DFeatureLayer(unittest.TestCase):
    def test_query_result_offset(self):
        """
        Test query result_offset
        """
        result_offset_results = layer.query_3d(result_offset=1)
        assert result_offset_results

    def test_query_object_ids(self):
        """
        Test query object_ids
        """
        object_ids_result = layer.query_3d(object_ids="10,20,30")
        assert isinstance(object_ids_result, dict)
        assert len(object_ids_result["features"]) == 0

    def test_query_out_fields(self):
        """ "
        Test query with limited out_fields indicated
        Test return_distinct_values
        """
        fields = layer.query_3d(out_fields=["ESRI3DO_OY", "ESRI3DO_TZ", "ESRI3DO_RDEG"])
        # ObjectId field always included
        assert len(fields["fields"]) == 4

        distinct_values = layer.query_3d(
            out_fields=["ESRI3DO_OY", "ESRI3DO_TZ", "ESRI3DO_RDEG"],
            return_distinct_values=True,
        )
        # ObjectId field not included
        assert len(distinct_values["fields"]) == 3

    def test_query_order_by_fields(self):
        """ "
        Test query with order_by_fields=True
        """
        ordered = layer.query_3d(
            out_fields=["ESRI3DO_OY", "ESRI3DO_TZ", "ESRI3DO_RDEG"],
            order_by_fields="ESRI3DO_OY ASC, ESRI3DO_TZ DESC, ESRI3DO_RDEG ASC",
        )
        assert ordered

    def test_query_all_records(self):
        """ "
        Test query with return_all_records=False. ! In this case we only have one feature...
        """
        limit_records = layer.query_3d(result_record_count=2000)
        all_records = layer.query_3d()

        assert len(limit_records) == len(all_records)
        assert limit_records

    def test_query_historic_moments_and_time(self):
        """ "
        Test query with historic_moments parameter
        Test query with time_filter parameter
        """
        historic = layer.query_3d(historic_moment=1199145600000)
        assert historic

        time_filter_results = layer.query_3d(time_filter=[1199145600000, 1230768000000])
        assert time_filter_results

    def test_query_sql_format(self):
        """ "
        Test query with sql_format
        """
        sql = layer.query_3d(sql_format="standard")
        assert sql

    def test_query_units(self):
        """ "
        Test query with different units
        """
        km = layer.query_3d(units="esriSRUnit_Kilometer")
        foot = layer.query_3d(units="esriSRUnit_Foot")
        nautical = layer.query_3d(units="esriSRUnit_USNauticalMile")

        assert km
        assert foot
        assert nautical

    def test_query_geometry_filter(self):
        """ "
        Test query with geometry_filter
        """
        geom_filter = layer.query_3d(
            geometry_filter={
                "xmin": -13228997.10497058,
                "ymin": 3961002.843403707,
                "xmax": -13014973.425772188,
                "ymax": 4113876.899973986,
                "spatialReference": {"wkid": 4326},
            }
        )
        assert geom_filter["spatialReference"]["wkid"] == 4326

    def test_query_group_by_field(self):
        """ "
        Test query with group_by_field_for_statistics
        """
        group_field = layer.query_3d(
            group_by_fields_for_statistics="ESRI3DO_RDEG, ESRI3DO_OY"
        )
        assert group_field


if __name__ == "__main__":
    unittest.main()
