import unittest
from unittest.case import SkipTest
import os
import uuid
import tempfile
import pandas as pd
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging


enable_verbose_logging()
test_data = [
    {
        'id': 1,
        'location_id': 1,
        'address_1': '2600 Middlefield Road',
        'address_2': None,
        'city': 'Redwood City',
        'state_province': 'CA',
        'postal_code': '94063',
        'country': 'US',
    },
    {
        'id': 2,
        'location_id': 2,
        'address_1': '24 Second Avenue',
        'address_2': None,
        'city': 'San Mateo',
        'state_province': 'CA',
        'postal_code': '94401',
        'country': 'US',
    },
    {
        'id': 3,
        'location_id': 3,
        'address_1': '24 Second Avenue',
        'address_2': None,
        'city': 'San Mateo',
        'state_province': 'CA',
        'postal_code': '94403',
        'country': 'US',
    },
    {
        'id': 4,
        'location_id': 4,
        'address_1': '24 Second Avenue',
        'address_2': None,
        'city': 'San Mateo',
        'state_province': 'CA',
        'postal_code': '94401',
        'country': 'US',
    },
    {
        'id': 5,
        'location_id': 5,
        'address_1': '24 Second Avenue',
        'address_2': None,
        'city': 'San Mateo',
        'state_province': 'CA',
        'postal_code': '94401',
        'country': 'US',
    },
    {
        'id': 6,
        'location_id': 6,
        'address_1': '800 Middle Avenue',
        'address_2': None,
        'city': 'Menlo Park',
        'state_province': 'CA',
        'postal_code': '94025-9881',
        'country': 'US',
    },
    {
        'id': 7,
        'location_id': 7,
        'address_1': '500 Arbor Road',
        'address_2': None,
        'city': 'Menlo Park',
        'state_province': 'CA',
        'postal_code': '94025',
        'country': 'US',
    },
    {
        'id': 8,
        'location_id': 8,
        'address_1': '800 Middle Avenue',
        'address_2': None,
        'city': 'Menlo Park',
        'state_province': 'CA',
        'postal_code': '94025-9881',
        'country': 'US',
    },
    {
        'id': 9,
        'location_id': 9,
        'address_1': '2510 Middlefield Road',
        'address_2': None,
        'city': 'Redwood City',
        'state_province': 'CA',
        'postal_code': '94063',
        'country': 'US',
    },
    {
        'id': 10,
        'location_id': 10,
        'address_1': '1044 Middlefield Road',
        'address_2': None,
        'city': 'Redwood City',
        'state_province': 'CA',
        'postal_code': '94063',
        'country': 'US',
    },
    {
        'id': 11,
        'location_id': 11,
        'address_1': '2140 Euclid Avenue.',
        'address_2': None,
        'city': 'Redwood City',
        'state_province': 'CA',
        'postal_code': '94061',
        'country': 'US',
    },
    {
        'id': 12,
        'location_id': 12,
        'address_1': '1044 Middlefield Road',
        'address_2': '2nd Floor',
        'city': 'Redwood City',
        'state_province': 'CA',
        'postal_code': '94063',
        'country': 'US',
    },
    {
        'id': 13,
        'location_id': 13,
        'address_1': '399 Marine Parkway.',
        'address_2': None,
        'city': 'Redwood City',
        'state_province': 'CA',
        'postal_code': '94065',
        'country': 'US',
    },
    {
        'id': 14,
        'location_id': 14,
        'address_1': '660 Veterans Blvd.',
        'address_2': None,
        'city': 'Redwood City',
        'state_province': 'CA',
        'postal_code': '94063',
        'country': 'US',
    },
    {
        'id': 15,
        'location_id': 15,
        'address_1': '1500 Valencia Street',
        'address_2': None,
        'city': 'San Francisco',
        'state_province': 'CA',
        'postal_code': '94110',
        'country': 'US',
    },
    {
        'id': 16,
        'location_id': 16,
        'address_1': '1161 South Bernardo',
        'address_2': None,
        'city': 'Sunnyvale',
        'state_province': 'CA',
        'postal_code': '94087',
        'country': 'US',
    },
    {
        'id': 17,
        'location_id': 17,
        'address_1': '409 South Spruce Avenue',
        'address_2': None,
        'city': 'South San Francisco',
        'state_province': 'CA',
        'postal_code': '94080',
        'country': 'US',
    },
    {
        'id': 18,
        'location_id': 18,
        'address_1': '114 Fifth Avenue',
        'address_2': None,
        'city': 'Redwood City',
        'state_province': 'CA',
        'postal_code': '94063',
        'country': 'US',
    },
    {
        'id': 19,
        'location_id': 19,
        'address_1': '19 West 39th Avenue',
        'address_2': None,
        'city': 'San Mateo',
        'state_province': 'CA',
        'postal_code': '94403',
        'country': 'US',
    },
    {
        'id': 20,
        'location_id': 21,
        'address_1': '123 El Camino Real',
        'address_2': None,
        'city': 'Belmont',
        'state_province': 'CA',
        'postal_code': '94002',
        'country': 'US',
    },
    {
        'id': 21,
        'location_id': 22,
        'address_1': '2013 Avenue of the fellows',
        'address_2': 'Suite 100',
        'city': 'San Francisco',
        'state_province': 'CA',
        'postal_code': '94103',
        'country': 'US',
    },
]


@profiles.enterprise_and_agol
@integration_test
class TestImportTable(unittest.TestCase):
    """Tests the import_table logic"""

    @classmethod
    def setUpClass(cls):
        cls.df = pd.DataFrame(data=test_data)

    def test_assert_error(self):
        """tests that the assertion error is raised"""
        content = self.gis.content
        with self.assertRaises(Exception) as context:
            content.import_table("figgypudding", "streetcars")

    def test_import_table_with_defaults(self):
        """import table task with all defaults"""
        content = self.gis.content
        pitem = content.import_table(df=self.df)
        source_items = pitem.related_items(
            rel_type="Service2Data", direction='forward'
        )
        assert len(source_items) > 0
        assert "Import Table created on" in pitem.title
        assert "import_table_" in pitem.url
        assert len(pitem.tables) > 0
        assert pitem.delete(permanent=True)
        [item.delete(permanent=True) for item in source_items]

    def test_import_table_with_service_name(self):
        """simple import table task with service name"""
        content = self.gis.content
        pitem = content.import_table(
            df=self.df, service_name=f"test_import_table_service_name_{uuid.uuid4().hex[:5]}"
        )
        source_items = pitem.related_items(
            rel_type="Service2Data", direction='forward'
        )
        assert source_items[0].type == "CSV"
        assert len(source_items) > 0
        assert "Import Table created on" in pitem.title
        assert "test_import_table_service_name" in pitem.url
        assert len(pitem.tables) > 0
        assert pitem.delete(permanent=True)
        [item.delete(permanent=True) for item in source_items]

    def test_import_table_publish_params(self):
        """simple import table task with publish params"""
        content = self.gis.content
        folder = self.gis.content.folders._get_or_create(
            folder="integration_testing_import_table",
            owner=self.gis._username,
        )
        fname = os.path.join(
            tempfile.gettempdir(), uuid.uuid4().hex[:4] + ".csv"
        )
        self.df.to_csv(fname)
        aitem = folder.add(
            file=fname,
            item_properties={
                "type": "CSV",
                "title": "test_import_table_publish_params_csv",
            },
        ).result()
        analyzed = content.analyze(item=aitem, file_type='csv')
        pp = analyzed['publishParameters']
        pp['locationType'] = "none"
        pp['name'] = f"A{uuid.uuid4().hex[:5]}Z".upper()

        pitem = content.import_table(
            df=self.df,
            service_name=f"test_import_table_publish_params_{uuid.uuid4().hex[:5]}",
            publish_parameters=pp,
            title='test_import_table_publish_params',
        )
        source_items = pitem.related_items(
            rel_type="Service2Data", direction='forward'
        )
        assert len(source_items) > 0
        assert len(pitem.tables) > 0
        assert "test_import_table_publish_params" in pitem.title
        assert aitem.delete(permanent=True)
        assert pitem.delete(permanent=True)
        [item.delete(permanent=True) for item in source_items]

    @SkipTest("Run manually in gdal env")
    def test_import_table_gdal(self):
        """If gdal is present in the environment, it will be used to publish a filegeodatabase rather than a csv"""
        content = self.gis.content
        pitem = content.import_table(
            df=self.df, service_name=f"test_import_table_service_name_{uuid.uuid4().hex[:5]}"
        )
        source_items = pitem.related_items(
            rel_type="Service2Data", direction='forward'
        )
        assert source_items[0].type == "File Geodatabase"
        assert len(source_items) > 0
        assert "Import Table created on" in pitem.title
        assert "test_import_table_service_name" in pitem.url
        assert len(pitem.tables) > 0
        assert pitem.delete(permanent=True)
        [item.delete(permanent=True) for item in source_items]
if __name__ == "__main__":
    unittest.main()
