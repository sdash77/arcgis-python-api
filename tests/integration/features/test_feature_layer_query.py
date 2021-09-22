from logging import raiseExceptions
import sys
import unittest
from arcgis import geometry

sys.path.insert(0, r"C:\\ipython_workfolder\\geosaurus_main\src")

from arcgis.features.layer import FeatureLayer
from arcgis.gis import GIS

gis = GIS(profile="your_online_profile")

# Major cities point layer
item = gis.content.get("17eaf8891efe4887a0bb9e265c34afb0")
layer = item.layers[0]
print(layer)


class TestQueryFeatureLayer(unittest.TestCase):
    def test_query_count_only(self):
        """ "
        Test query with return_count_only=True
        """
        count = layer.query(return_count_only=True)
        assert isinstance(count, int)
        assert count > 0

    def test_query_ids_only(self):
        """ "
        Test query with return_ids_only=True
        """
        ids = layer.query(return_ids_only=True)
        assert isinstance(ids, dict)
        assert "objectIds" in ids
        assert "objectIdFieldName" in ids

    def test_query_geometries(self):
        """ "
        Test query with return geometries = True and then False
        """
        geometry_true = layer.query(return_geometry=True)
        assert geometry_true.features[0].geometry

        geometry_false = layer.query(return_geometry=False)
        assert geometry_false.features[0].geometry is None

    def test_query_out_fields(self):
        """ "
        Test query with limited out_fields indicated
        Test return_distinct_values
        """
        fields = layer.query(out_fields=["class", "families", "females"])
        # ObjectId field always included
        assert len(fields.fields) == 4

        distinct_values = layer.query(
            out_fields=["class", "families", "females"], return_distinct_values=True
        )
        # ObjectId field not included
        assert len(distinct_values.fields) == 3

    def test_query_extent_only(self):
        """ "
        Test query with return_extent_only=True
        """
        extent = layer.query(return_extent_only=True)
        assert extent["extent"]
        assert isinstance(extent, dict)
        assert extent["extent"]["spatialReference"]

    def test_query_order_by_fields(self):
        """ "
        Test query with order_by_fields=True
        """
        ordered = layer.query(
            out_fields=["class", "families", "females"],
            order_by_fields="families ASC, females DESC, class ASC",
        )
        assert ordered

    def test_query_return_m_and_z(self):
        """ "
        Test query with return_m and return_z
        """
        all_coord_item = gis.content.get("301df20a74b841c7b18b40a6673ff4e6")
        coord_layer = all_coord_item.layers[0]

        return_m = coord_layer.query(return_m=True)
        assert return_m.has_m

        return_z = coord_layer.query(return_z=True)
        assert return_z.has_z

        m_and_z = coord_layer.query(return_z=True, return_m=True)
        assert m_and_z.has_m
        assert m_and_z.has_z

    def test_query_all_records(self):
        """ "
        Test query with return_all_records=False
        """
        limit_records = layer.query(return_all_records=False)
        all_records = layer.query()

        assert len(limit_records) < len(all_records)
        assert limit_records

    def test_query_historic_moments(self):
        """ "
        Test query with historic_moments parameter
        """
        layer_1 = gis.content.get("5183636f099c48789628226e5730fb13").layers[0]
        historic = layer_1.query(historic_moment=3)
        assert historic

    def test_query_sql_format(self):
        """ "
        Test query with sql_format
        """
        sql = layer.query(sql_format="standard")
        assert sql

    def test_query_units(self):
        """ "
        Test query with different units
        """
        km = layer.query(units="esriSRUnit_Kilometer")
        foot = layer.query(units="esriSRUnit_Foot")
        nautical = layer.query(units="esriSRUnit_USNauticalMile")

        assert km
        assert foot
        assert nautical

    def test_query_geometry_filter(self):
        """ "
        Test query with geometry_filter
        """
        geom_filter = layer.query(
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
        """ "
        Test query with group_by_field_for_statistics
        """
        group_field = layer.query(group_by_fields_for_statistics="females, families")
        assert group_field

    def test_query_out_statistics(self):
        """ "
        Test query with out_statistics
        """
        output_name = "female_count"
        out_stats = layer.query(
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
