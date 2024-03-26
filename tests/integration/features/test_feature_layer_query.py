import os
import unittest

from arcgis.gis import GIS
from utils.decorators import integration_test

gis = GIS(profile="your_online_profile", verify_cert=False)

# Major cities point layer
try:
    pitem = gis.content.search(
        "major_cities owner:{username}".format(username=gis.users.me.username),
        "Feature Layer",
    )[0]
    assert pitem
except:
    fp = "./major_cities.zip"
    if os.path.isfile(path=fp):
        item = gis.content.add(
            item_properties={
                "title": "major_cities",
                "type": "File Geodatabase",
            },
            data=fp,
        )
        pitem = item.publish()
    else:
        raise Exception("major_cities not found")

layer = pitem.layers[0]
print(layer)


@integration_test
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

    def test_query_result_offset(self):
        """
        Test query result_offset
        """
        result_offset_results = layer.query(result_offset=100, return_all_records=False)
        assert result_offset_results
        assert result_offset_results.features[0].attributes["OBJECTID"] == 101

    def test_query_object_ids(self):
        """
        Test query object_ids
        """
        object_ids_result = layer.query(object_ids="10,20,30")
        assert object_ids_result
        assert len(object_ids_result) == 3

    def test_query_as_df(self):
        """
        Test query as_df
        """
        import pandas as pd

        df = layer.query(as_df=True)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

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

    def test_query_return_m_and_z_and_centroid(self):
        """ "
        Test query with return_m and return_z
        Test query with return_centroid
        """
        try:
            all_coord_item = gis.content.search("Jordan_Aviation")[1]
            assert all_coord_item
        except:
            fp = "./jordan_aviation"
            if os.path.isfile(path=fp):
                all_coord_item = gis.content.add(
                    item_properties={
                        "title": "Jordan_Aviation",
                        "type": "File Geodatabase",
                    },
                    data=fp,
                )
                item.publish()

        coord_layer = all_coord_item.layers[0]

        return_m = coord_layer.query(return_m=True)
        assert return_m.has_m

        return_z = coord_layer.query(return_z=True)
        assert return_z.has_z

        m_and_z = coord_layer.query(return_z=True, return_m=True)
        assert m_and_z.has_m
        assert m_and_z.has_z

        # polygon layer
        centroid_results = all_coord_item.layers[2].query(return_centroid=True)
        assert centroid_results

    def test_query_all_records(self):
        """ "
        Test query with return_all_records=False
        """
        limit_records = layer.query(return_all_records=False, result_record_count=2000)
        all_records = layer.query()

        assert len(limit_records) < len(all_records)
        assert limit_records

    def test_query_historic_moments_and_time(self):
        """ "
        Test query with historic_moments parameter
        Test query with time_filter parameter
        """
        try:
            pitem = gis.content.search(
                "Traffic Collisions owner:{username}".format(
                    username=gis.users.me.username
                )
            )[0]
        except:
            fp = "./traffic_collisions"
            if os.path.isfile(path=fp):
                item = gis.content.add(
                    item_properties={
                        "title": "traffic_collisions",
                        "type": "File Geodatabase",
                    },
                    data=fp,
                )
                pitem = item.publish()
        layer_1 = pitem.layers[0]
        historic = layer_1.query(historic_moment=1199145600000)
        assert historic

        time_filter_results = layer.query(time_filter=[1199145600000, 1230768000000])
        assert time_filter_results

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
