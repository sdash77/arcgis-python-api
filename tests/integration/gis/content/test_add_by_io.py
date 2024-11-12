import unittest
import io
import uuid
import pandas as pd
import requests
from arcgis.gis import Item
from utils.decorators import integration_test, profiles


@profiles.all
@integration_test
class TestAddUsingIO(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.folder = cls.gis.content.folders._get_or_create(
            folder="integration_testing_gis_content_add_by_io",
            owner=cls.gis._username
        )

        GUID = uuid.uuid4().hex[:6]
        cls.item_properties = {
            "type": "CSV",
            "title": f"IOTest{GUID}",
            "fileName": f"io_{GUID}_test.csv",
            "tags": "integration_testing"
        }

        # setup io data
        URL = (
            "https://raw.githubusercontent.com/jbrownlee/Datasets/master/airline-passengers.csv"
        )
        input = requests.get(URL).text
        input_io = io.StringIO(input)
        cls.data = pd.read_csv(input_io)
        cls.output = io.StringIO()
        cls.data.to_csv(cls.output, index=False)

    @classmethod
    def tearDownClass(cls):
        if cls.folder:
            cls.folder.delete(permanent=True)

    def test_add_by_string_io(self):
        """adds the CSV file using stringIO object"""
        item = self.folder.add(self.item_properties, file=self.output).result()
        assert isinstance(item, Item)
        assert item.type == "CSV"
        assert item.delete(permanent=True)

    def test_update_by_string_io(self):
        """adds the CSV file using stringIO object"""
        item = self.folder.add(self.item_properties, file=self.output).result()
        assert isinstance(item, Item)
        try:
            assert item.update(data=self.output)
        except Exception as e:
            raise e
        finally:
            if item:
                assert item.delete(permanent=True)


if __name__ == "__main__":
    unittest.main()
