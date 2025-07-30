import unittest
from arcgis.gis import GIS
from arcgis.features import FeatureLayer, FeatureSet
from arcgis.geometry import Envelope, Geometry
from arcgis.geometry.filters import intersects
from utils.decorators import integration_test, profiles


# TODO: get better service with more features to be able to test better. Placeholder service
## Test layer in ArcGIS Enterprse
# A Scene Layer with Associated Feature Layer can only be published from ArcGIS Pro
# source_ppkx file: //qalab_server/pydata/v109/geosaurus/features_mod_FeatureLayerQuery/3do_feature_layer/ned_3do_flyr.ppkx
# layer used in testing for 11.3
# layer = FeatureLayer(
# "https://rpubs22301.ags.esri.com/server/rest/services/Hosted/NED_buildings/FeatureServer/0"
# )


@unittest.skip("Need to recreate the data in both AGOL and Enterprise")
@profiles.admin_enterprise
@integration_test
class TestQuery3DFeatureLayer(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """
        get test data
        """
        ned_3do_item = cls.gis.content.search(
            query="title:NED_buildings AND tags:integration_testing",
            item_type="Feature Layer",
        )[0]
        cls.ned_3do_layer = ned_3do_item.layers[0]

    def test_query_result_offset(self):
        """
        Test query result_offset
        """
        result_offset_results = self.ned_3do_layer.query_3d(
            result_offset=10,
            order_by_fields="objectid ASC",
            out_fields="objectid, esri3do_ox, esri3do_oy, esri3do_oz",
        )
        assert len(result_offset_results["features"]) == 84
        assert result_offset_results["features"][0]["attributes"]["objectid"] == 11

    def test_query_object_ids(self):
        """
        Test query object_ids
        """
        object_ids_result = self.ned_3do_layer.query_3d(
            object_ids="10,20,30",
            out_fields="objectid, esri3do_ox, esri3do_oy, esri3do_oz",
        )
        oid_list = [o["attributes"]["objectid"] for o in object_ids_result["features"]]
        oid_list.sort()
        assert oid_list == [10, 20, 30]
        assert isinstance(object_ids_result, dict)
        assert len(object_ids_result["features"]) == 3

    def test_query_out_fields(self):
        """
        Test query with limited out_fields indicated
        Test return_distinct_values
        """
        fields = self.ned_3do_layer.query_3d(
            where="objectid < 5", out_fields=["esri3do_ox", "esri3do_oy", "esri3do_oz"]
        )
        # ObjectId field always included
        assert len(fields["fields"]) == 4
        assert len(fields["features"]) == 4
        field_list = [f["name"] for f in fields["fields"]]
        for out_field in ["esri3do_ox", "esri3do_oy", "esri3do_oz"]:
            assert out_field in field_list

    def test_query_order_by_fields(self):
        """
        Test query with order_by_fields=True
        """
        ordered = self.ned_3do_layer.query_3d(
            out_fields=["esri3do_ox", "esri3do_oy", "esri3do_oz", "esri3do_rdeg"],
            order_by_fields="esri3do_oz ASC",
        )
        assert ordered
        assert (
            ordered["features"][0]["attributes"]["esri3do_oz"]
            <= ordered["features"][1]["attributes"]["esri3do_oz"]
        )
        assert (
            ordered["features"][-2]["attributes"]["esri3do_oz"]
            <= ordered["features"][-1]["attributes"]["esri3do_oz"]
        )

    def test_query_all_records(self):
        """
        Test query with return_all_records=False. ! In this case we only have 94 features...
        """
        limit_records = self.ned_3do_layer.query_3d(where="OBJECTID < 43")
        all_records = self.ned_3do_layer.query_3d()

        assert limit_records
        assert len(limit_records["features"]) < len(all_records["features"])
        assert limit_records.get("assetMapFields")

    def test_query_historic_moments_and_time(self):
        """
        Test query with historic_moments parameter
        Test query with time_filter parameter
        """
        if self.ned_3do_layer.properties["isDataArchived"]:
            start_moment = self.ned_3do_layer.properties["archivingInfo"][
                "startArchivingMoment"
            ]

        historic = self.ned_3do_layer.query_3d(
            where="1=1", historic_moment=start_moment
        )
        assert len(historic["features"]) == 94

        time_filter_results = self.ned_3do_layer.query_3d(
            where="OBJECTID = 12",
            time_filter=[start_moment, start_moment + (86400000 * 4)],
            out_fields="objectid, esri3do_ox, esri3do_oy, esri3do_oz",
        )
        assert time_filter_results
        assert time_filter_results["features"][0]["attributes"]["objectid"] == 12

    def test_query_sql_format(self):
        """
        Test query with sql_format
        """
        sql = self.ned_3do_layer.query_3d(sql_format="standard")
        assert sql
        assert sql["assetMapFields"]
        assert len(sql["features"]) == 94

    def test_query_units(self):
        """
        Test query with different units
        """
        pt_geom = Geometry(
            iterable={"x": 172800, "y": 451600, "spatialReference": {"wkid": 28992}}
        )
        km = self.ned_3do_layer.query_3d(
            geometry_filter=pt_geom, distance=0.1, units="esriSRUnit_Kilometer"
        )
        foot = self.ned_3do_layer.query_3d(
            geometry_filter=pt_geom, distance=100, units="esriSRUnit_Foot"
        )
        nautical = self.ned_3do_layer.query_3d(
            geometry_filter=pt_geom, distance=0.05, units="esriSRUnit_StatuteMile"
        )

        assert len(km["features"]) < 94
        assert len(foot["features"]) < 94
        assert len(nautical["features"]) < 94

    def test_query_geometry_filter(self):
        """
        Test query with geometry_filter
        """

        geom_env = Envelope(
            {
                "xmin": 172726.4278,
                "ymin": 451614.2502,
                "xmax": 172829.4118,
                "ymax": 451657.2589,
                "spatialReference": {"wkid": 28992},
            }
        )
        sr = {"wkid": 28992}
        geom_filt = intersects(geom_env, sr)

        geom_filter = self.ned_3do_layer.query_3d(geometry_filter=geom_filt)

        assert geom_filter["spatialReference"]["wkid"] == 28992
        assert len(geom_filter["features"]) < len(
            self.ned_3do_layer.query_3d()["features"]
        )

    # query doesn't return expected results on rest api
    # def test_query_group_by_field(self):
    # """
    # Test query with group_by_field_for_statistics
    # """
    # group_field = self.ned_3do_layer.query_3d(
    # format_3d_objects="3D_dae",
    # out_statistics=[
    # {
    # "statisticType": "sum",
    # "onStatisticField": "story",
    # "outStatisticFieldName": "total_stories",
    # }
    # ],
    # group_by_fields_for_statistics="description",
    # )
    # assert group_field.features[0]["total_stories"]
    # assert len(group_field.features) < len(self.ned_3do_layer.query()["features"])


if __name__ == "__main__":
    unittest.main()
