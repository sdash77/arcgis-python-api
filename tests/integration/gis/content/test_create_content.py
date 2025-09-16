import unittest
from utils.decorators import integration_test, profiles
from integration.config import get_resource_path
from utils.data_utils import INTEGRATION_TEST_ITEM_TAG, cleanup_published_items
import pandas as pd
from arcgis.features import FeatureCollection
import uuid
from arcgis.gis import Item


@profiles.all
@integration_test
class TestContentManager(unittest.TestCase):
    """Test ContentManager import_data and create_service"""

    @classmethod
    def setUpClass(cls):
        """Get test data"""
        cls.add_csv_path = get_resource_path(
            "staging_data/dino_ContentManager_test_add_csv.csv", unique_copy=True
        )
        cls.import_data_geocode_path = get_resource_path(
            "staging_data/dino_ContentManager_test_import_data_geocode.csv", unique_copy=True
        )
        cls.import_data_geocode_html_path = get_resource_path(
            "staging_data/estimated_guns_by_country.html", unique_copy=True
        )

        cls.df = pd.read_csv(cls.import_data_geocode_path)

    def tearDown(self):
        if isinstance(self.output, Item):
            cleanup_published_items([self.output])

    def test_create_service_defaults(self):
        """test create_service with default parameters"""
        service_title = f"test_create_service_{uuid.uuid4().hex[:5]}"
        self.output = self.gis.content.create_service(
            name=service_title, service_description="create_default_service"
        )
        self.assertEqual(
            self.output.title, service_title, "Service title does not match"
        )
        self.assertEqual(
            self.output.type, "Feature Service", "Default service type created is not a feature service"
        )

    def test_create_service_with_access(self):
        """Access test for create service"""
        service_title = f"test_create_service_access_{uuid.uuid4().hex[:5]}"
        self.output = self.gis.content.create_service(
            name=service_title, item_properties={"access": "org"}
        )
        self.assertEqual(
            self.output.title, service_title, "Service title does not match"
        )
        self.assertEqual(
            self.output.type, "Feature Service", "Default service type created is not a feature service"
        )

    def test_import_data_geocode(self):
        """test import_data with address_field parameter"""
        self.output = self.gis.content.import_data(self.df, {"Address": "LOCATION"}, tags=INTEGRATION_TEST_ITEM_TAG)
        self.assertIsInstance(
            self.output, FeatureCollection,
            "import_data does not return a Feature Collection upon success. Instead it returns: " + str(type(self.output)),
        )
        self.assertTrue(
            len(self.output.layer.featureSet.features) > 0,
            "No features found in geocoded" "feature collection",
        )

    def test_import_data_geocode_from_html(self):
        df = pd.read_html(self.import_data_geocode_html_path)[0]

        # data engineering to clean/restructure dataframe
        df.columns = df.columns.str.replace(" ", "_")
        df.rename(columns={"Unnamed:_0": "id_number"}, inplace=True)
        df.drop(labels=0, axis=0, inplace=True)
        df.reset_index(drop=True, inplace=True)

        # geocode and publish
        self.output = self.gis.content.import_data(
            df, {"CountryCode": "Country_or_subnational_area"}, tags=INTEGRATION_TEST_ITEM_TAG
        )

        self.assertIsInstance(
            self.output, FeatureCollection,
            "import_data does not return a Feature Collection upon success. Instead it returns: " + str(
                type(self.output)),
        )
        self.assertTrue(
            len(self.output.layer.featureSet.features) > 0, "No features found in geocoded" "feature collection",
        )


if __name__ == "__main__":
    unittest.main()
