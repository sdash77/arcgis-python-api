import sys
import logging
import unittest
import os
import uuid
import tempfile
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
import pandas as pd
from utils.decorators import integration_test

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = [
    'your_enterprise_profile',
    'your_online_profile',
]
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)

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


@integration_test
class TestImportTable(unittest.TestCase):
    """Tests the import_table logic"""

    @classmethod
    def setUpClass(cls):
        cls.df = pd.DataFrame(data=test_data)
        cls.gis_objs = [
            GIS(profile=profile, proxy=PROXIES, verify_cert=False)
            for profile in profiles
        ]

    def test_assert_error(self):
        """tests that the assertion error is raised"""
        gis: GIS = None

        for gis in self.gis_objs:
            content = gis.content
            with self.assertRaises(Exception) as context:
                content.import_table("figgypudding", "streetcars")

    def test_import_table_with_defaults(self):
        """import table task with all defaults"""
        for gis in self.gis_objs:
            content = gis.content
            pitem = content.import_table(df=self.df)
            source_items = pitem.related_items(
                rel_type="Service2Data", direction='forward'
            )
            assert len(source_items) > 0
            assert pitem.title
            assert len(pitem.tables) > 0
            assert pitem.delete()
            [item.delete() for item in source_items]

    def test_import_table_with_service_name(self):
        """simple import table task"""
        for gis in self.gis_objs:
            content = gis.content
            pitem = content.import_table(
                df=self.df, service_name=f"a{uuid.uuid4().hex[:5]}b"
            )
            source_items = pitem.related_items(
                rel_type="Service2Data", direction='forward'
            )
            assert len(source_items) > 0
            assert pitem.title
            assert len(pitem.tables) > 0
            assert pitem.delete()
            [item.delete() for item in source_items]

    def test_import_table_pp(self):
        """simple import table task with publish parms"""
        for gis in self.gis_objs:
            content = gis.content
            fname = os.path.join(
                tempfile.gettempdir(), uuid.uuid4().hex[:4] + ".csv"
            )
            self.df.to_csv(fname)
            aitem = content.add(
                data=fname,
                item_properties={
                    "type": "CSV",
                    "title": uuid.uuid4().hex[:7],
                },
            )
            analyzed = content.analyze(item=aitem, file_type='csv')
            pp = analyzed['publishParameters']
            pp['locationType'] = "none"
            pp['name'] = f"A{uuid.uuid4().hex[:5]}Z".upper()

            pitem = content.import_table(
                df=self.df,
                service_name=f"a{uuid.uuid4().hex[:5]}b",
                publish_parameters=pp,
                title='(--CSV_TEST--)',
            )
            source_items = pitem.related_items(
                rel_type="Service2Data", direction='forward'
            )
            assert len(source_items) > 0
            assert len(pitem.tables) > 0
            assert pitem.delete()
            [item.delete() for item in source_items]


if __name__ == "__main__":
    unittest.main()
