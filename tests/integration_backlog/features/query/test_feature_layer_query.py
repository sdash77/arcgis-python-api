import unittest
from utils.decorators import integration_test, profiles
from arcgis.features import FeatureSet
from arcgis.geometry import Envelope, Geometry
from arcgis.geometry.filters import intersects
from arcgis.gis import GIS


# @profiles.enterprise_and_agol
@integration_test
class TestQueryFeatureLayer(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """
        get test data
        """
        proxies = {"http": "http://127.0.0.1:8999", "https": "http://127.0.0.1:8999"}
        cls.gis = GIS(
            profile="your_enterprise_profile", verify_cert=False, proxy=proxies
        )
        major_cities_item = cls.gis.content.search(
            "{item} tags:{tag}".format(item="major_cities", tag="integration_testing"),
            "Feature Layer",
        )[0]
        cls.major_cities_layer = major_cities_item.layers[0]

        jordan_aviation_item = cls.gis.content.search(
            "{item} tags:{tag}".format(
                item="jordan_aviation", tag="integration_testing"
            ),
            "Feature Layer",
        )[0]
        cls.coord_layer = jordan_aviation_item.layers[0]
        cls.coord_layer2 = jordan_aviation_item.layers[2]

        traffic_collisions_item = cls.gis.content.search(
            "{item} tags:{tag}".format(
                item="Traffic Collisions", tag="integration_testing"
            ),
            "Feature Layer",
        )[0]
        cls.historic_layer = traffic_collisions_item.layers[0]

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

    def test_query_geometry(self):
        """
        Test query with return geometries = True and then False
        """
        geometry_true = self.major_cities_layer.query(return_geometry=True)
        assert geometry_true.features[0].geometry
        assert "x" in list(geometry_true.features[0].geometry.keys())
        assert "y" in list(geometry_true.features[0].geometry.keys())

        geometry_false = self.major_cities_layer.query(return_geometry=False)
        assert geometry_false.features[0].geometry is None

        geom_df = self.major_cities_layer.query(
            where="class = 'city'", return_geometry=True, as_df=True
        )
        assert isinstance(geom_df.loc[0].SHAPE, Geometry)

    def test_query_result_offset(self):
        """
        Test query result_offset
        """
        base_query = result_offset_results = self.major_cities_layer.query(
            return_all_records=False
        )
        count_base_records = len(base_query.features)
        result_offset_results = self.major_cities_layer.query(
            result_offset=100, return_all_records=False
        )
        count_offset_records = len(result_offset_results.features)

        assert result_offset_results
        assert (count_base_records - count_offset_records) == 100

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
        field_names = ["population", "class", "pop_class"]
        if self.gis._is_arcgisonline:
            field_names = [n.upper() for n in field_names]
        fields = self.major_cities_layer.query(out_fields=field_names)
        # ObjectId field always included
        assert len(fields.fields) == 4

    def test_query_distinct_values(self):
        distinct_values = self.major_cities_layer.query(
            out_fields=["class"],
            return_distinct_values=True,
            return_geometry=False,
        )
        all_count = self.major_cities_layer.query(return_count_only=True)
        # ObjectId field not included
        assert len(distinct_values.fields) == 1
        assert (
            len(distinct_values.features) < all_count
        ), f"Incorrect difference. {len(distinct_values.features)} got {all_count}"

    def test_query_extent_only(self):
        """
        Test query with return_extent_only=True
        """
        extent = self.major_cities_layer.query(
            where="NAME = 'San Diego'", return_extent_only=True
        )
        assert extent["extent"]
        assert isinstance(extent, dict)
        assert extent["extent"]["spatialReference"]

    def test_query_order_by_fields(self):
        """
        Test query with order_by_fields=True
        """
        population_field_name = "population"
        field_names = ["population", "name", "pop_class"]
        if self.gis._is_arcgisonline:
            population_field_name = population_field_name.upper()
            field_names = [n.upper() for n in field_names]
        ordered = self.major_cities_layer.query(
            out_fields=field_names,
            order_by_fields=f"{population_field_name} ASC",
            return_geometry=False,
        )
        assert ordered
        assert (
            ordered.features[0].attributes[population_field_name]
            < ordered.features[1].attributes[population_field_name]
        )
        assert (
            ordered.features[1].attributes[population_field_name]
            < ordered.features[2].attributes[population_field_name]
        )

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

    def test_query_sql_format(self):
        """
        Test query with sql_format
        """
        name_field_name = "name"
        if self.gis._is_arcgisonline:
            name_field_name = name_field_name.upper()
        sql = self.major_cities_layer.query(
            where="name like '%Diego'", sql_format="standard"
        )
        assert sql
        assert sql.features[0].attributes[name_field_name].endswith("Diego")
        assert len(sql.features) < self.major_cities_layer.query(return_count_only=True)

    def test_query_units(self):
        """
        Test query with different units
        """
        sr = self.major_cities_layer.properties.extent["spatialReference"]
        ext1 = Envelope(
            iterable={
                "xmin": -12331108.041,
                "ymin": 4309825.403,
                "xmax": -11417150.495,
                "ymax": 4941634.769,
                "spatialReference": sr,
            }
        )

        gfilter = intersects(ext1, sr)

        km = self.major_cities_layer.query(
            geometry_filter=gfilter, distance=75, units="esriSRUnit_Kilometer"
        )
        foot = self.major_cities_layer.query(
            geometry_filter=gfilter, distance=1000, units="esriSRUnit_Foot"
        )
        nautical = self.major_cities_layer.query(
            geometry_filter=gfilter, distance=5, units="esriSRUnit_USNauticalMile"
        )

        assert km
        assert len(km.features) < self.major_cities_layer.query(return_count_only=True)
        assert foot
        assert len(foot.features) < self.major_cities_layer.query(
            return_count_only=True
        )
        assert nautical
        assert len(nautical.features) < self.major_cities_layer.query(
            return_count_only=True
        )

    def test_query_geometry_filter(self):
        """
        Test query with geometry_filter
        """
        geom_env = Envelope(
            iterable={
                "xmin": -10687568.614261,
                "ymin": 3822997.969683,
                "xmax": -9587687.5503808,
                "ymax": 4379803.502226,
                "spatialReference": {"wkid": 102100},
            }
        )

        geom_filter = self.major_cities_layer.query(
            geometry_filter=intersects(geom_env, sr={"wkid": 102100})
        )
        assert (
            geom_filter.spatial_reference["wkid"]
            is not geom_filter.spatial_reference["latestWkid"]
        )
        assert len(geom_filter.features) < self.major_cities_layer.query(
            return_count_only=True
        )

    def test_query_group_by_field(self):
        """
        Test query with group_by_field_for_statistics
        """
        population_field_name = "population"
        if self.gis._is_arcgisonline:
            population_field_name = population_field_name.upper()

        group_field = self.major_cities_layer.query(
            out_statistics=[
                {"statisticType": "avg", "onStatisticField": population_field_name}
            ],
            group_by_fields_for_statistics=population_field_name,
        )
        assert group_field
        assert isinstance(group_field, FeatureSet)
        assert len(group_field.features) == 2000

    def test_query_out_statistics(self):
        """
        Test query with out_statistics
        """
        output_name = "sum_population"
        population_field_name = "population"

        if self.gis._is_arcgisonline:
            population_field_name = population_field_name.lower()

        out_stats = self.major_cities_layer.query(
            out_statistics=[
                {
                    "statisticType": "sum",
                    "onStatisticField": population_field_name,
                    "outStatisticFieldName": output_name,
                }
            ]
        )
        assert out_stats
        assert (
            out_stats.fields[0]["name"] == output_name
        ), f"Expected 'sum_population' got {output_name}"


if __name__ == "__main__":
    unittest.main()
