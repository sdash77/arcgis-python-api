import unittest
from utils.decorators import integration_test, profiles


@profiles.agol
@integration_test
class TestQueryFeatureLayer(unittest.TestCase):

    def setUp(self) -> None:
        """
        get test data
        """
        major_cities_item = self.gis.content.search(
            "{item} tags:{tag}".format(item="major_cities", tag="integration_testing"),
            "Feature Layer",
        )[0]
        self.major_cities_layer = major_cities_item.layers[0]

        jordan_aviation_item = self.gis.content.search(
            "{item} tags:{tag}".format(
                item="jordan_aviation", tag="integration_testing"
            ),
            "Feature Layer",
        )[0]
        self.coord_layer = jordan_aviation_item.layers[0]
        self.coord_layer2 = jordan_aviation_item.layers[2]

        traffic_collisions_item = self.gis.content.search(
            "{item} tags:{tag}".format(
                item="Traffic Collisions", tag="integration_testing"
            ),
            "Feature Layer",
        )[0]
        self.historic_layer = traffic_collisions_item.layers[0]

    def test_query_count_only(self):
        """
        Test query with return_count_only=True
        """
        count = self.major_cities_layer.query(return_count_only=True)
        assert isinstance(count, int)
        assert count > 0

    def test_query_ids_only(self):
        """
        Test query with return_ids_only=True
        """
        ids = self.major_cities_layer.query(return_ids_only=True)
        assert isinstance(ids, dict)
        assert "objectIds" in ids
        assert "objectIdFieldName" in ids

    def test_query_geometries(self):
        """
        Test query with return geometries = True and then False
        """
        geometry_true = self.major_cities_layer.query(return_geometry=True)
        assert geometry_true.features[0].geometry

        geometry_false = self.major_cities_layer.query(return_geometry=False)
        assert geometry_false.features[0].geometry is None

    def test_query_result_offset(self):
        """
        Test query result_offset
        """
        result_offset_results = self.major_cities_layer.query(
            result_offset=100, return_all_records=False
        )
        assert result_offset_results
        assert result_offset_results.features[0].attributes["OBJECTID"] == 101

    def test_query_object_ids(self):
        """
        Test query object_ids
        """
        object_ids_result = self.major_cities_layer.query(object_ids="10,20,30")
        assert object_ids_result
        assert len(object_ids_result) == 3

    def test_query_as_df(self):
        """
        Test query as_df
        """
        import pandas as pd

        df = self.major_cities_layer.query(as_df=True)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    def test_query_out_fields(self):
        """
        Test query with limited out_fields indicated
        Test return_distinct_values
        """
        fields = self.major_cities_layer.query(
            out_fields=["class", "families", "females"]
        )
        # ObjectId field always included
        assert len(fields.fields) == 4

        distinct_values = self.major_cities_layer.query(
            out_fields=["class", "families", "females"], return_distinct_values=True
        )
        # ObjectId field not included
        assert len(distinct_values.fields) == 3

    def test_query_extent_only(self):
        """
        Test query with return_extent_only=True
        """
        extent = self.major_cities_layer.query(return_extent_only=True)
        assert extent["extent"]
        assert isinstance(extent, dict)
        assert extent["extent"]["spatialReference"]

    def test_query_order_by_fields(self):
        """
        Test query with order_by_fields=True
        """
        ordered = self.major_cities_layer.query(
            out_fields=["class", "families", "females"],
            order_by_fields="families ASC, females DESC, class ASC",
        )
        assert ordered

    def test_query_return_m_and_z_and_centroid(self):
        """
        Test query with return_m and return_z
        Test query with return_centroid
        """

        return_m = self.coord_layer.query(return_m=True)
        assert return_m.has_m

        return_z = self.coord_layer.query(return_z=True)
        assert return_z.has_z

        m_and_z = self.coord_layer.query(return_z=True, return_m=True)
        assert m_and_z.has_m
        assert m_and_z.has_z

        # polygon layer
        centroid_results = self.coord_layer2.query(return_centroid=True)
        assert centroid_results

    def test_query_all_records(self):
        """
        Test query with return_all_records=False
        """
        limit_records = self.major_cities_layer.query(
            return_all_records=False, result_record_count=2000
        )
        all_records = self.major_cities_layer.query()

        assert len(limit_records) < len(all_records)
        assert limit_records

    def test_query_historic_moments_and_time(self):
        """
        Test query with historic_moments parameter
        Test query with time_filter parameter
        """
        historic = self.historic_layer.query(historic_moment=1199145600000)
        assert historic

        time_filter_results = self.historic_layer.query(
            time_filter=[1199145600000, 1230768000000]
        )
        assert time_filter_results

    def test_query_sql_format(self):
        """
        Test query with sql_format
        """
        sql = self.major_cities_layer.query(sql_format="standard")
        assert sql

    def test_query_units(self):
        """
        Test query with different units
        """
        km = self.major_cities_layer.query(units="esriSRUnit_Kilometer")
        foot = self.major_cities_layer.query(units="esriSRUnit_Foot")
        nautical = self.major_cities_layer.query(units="esriSRUnit_USNauticalMile")

        assert km
        assert foot
        assert nautical

    def test_query_geometry_filter(self):
        """
        Test query with geometry_filter
        """
        geom_filter = self.major_cities_layer.query(
            geometry_filter={
                "xmin": -13228997.10497058,
                "ymin": 3961002.843403707,
                "xmax": -13014973.425772188,
                "ymax": 4113876.899973986,
                "spatialReference": {"wkid": 102100},
            }
        )
        assert (
            geom_filter.spatial_reference["wkid"]
            is not geom_filter.spatial_reference["latestWkid"]
        )

    def test_query_group_by_field(self):
        """
        Test query with group_by_field_for_statistics
        """
        group_field = self.major_cities_layer.query(
            group_by_fields_for_statistics="females, families"
        )
        assert group_field

    def test_query_out_statistics(self):
        """
        Test query with out_statistics
        """
        output_name = "female_count"
        out_stats = self.major_cities_layer.query(
            out_statistics=[
                {
                    "statisticType": "count",
                    "onStatisticField": "females",
                    "outStatisticFieldName": output_name,
                }
            ]
        )
        assert out_stats
        assert out_stats.fields[0]["name"] == output_name


if __name__ == "__main__":
    unittest.main()
