import unittest
import io
import uuid
from arcgis.gis import GIS
import pandas as pd
import requests
from utils.decorators import integration_test

GUID = uuid.uuid4().hex[:6]
item_properties = {
    "type": "CSV",
    "title": f"IOTest{GUID}",
    "fileName": f"io_{GUID}_test.csv",
}
URL = (
    "https://raw.githubusercontent.com/jbrownlee/Datasets/master/airline-passengers.csv"
)
PROFILES = ["your_online_profile", "your_kubernetes_profile"]

@integration_test
class TestAddUsingIO(unittest.TestCase):
    def test_add_by_string_io(self):
        """adds the CSV file using stringIO object"""
        input = requests.get(URL).text
        input_io = io.StringIO(input)
        data = pd.read_csv(input_io)
        output = io.StringIO()
        data.to_csv(output, index=False)
        gis = GIS(profile=PROFILES[0], verify_cert=False, trust_env=True)
        item = gis.content.add(item_properties, data=output)
        assert item
        assert item.delete()

    def test_update_by_string_io(self):
        """adds the CSV file using stringIO object"""
        input = requests.get(URL).text
        input_io = io.StringIO(input)
        data = pd.read_csv(input_io)
        output = io.StringIO()
        data.to_csv(output, index=False)
        gis = GIS(profile=PROFILES[0], verify_cert=False, trust_env=True)
        item = gis.content.add(item_properties, data=output)
        assert item
        try:
            assert item.update(data=output)
        except Exception as e:
            raise e
        finally:
            if item:
                assert item.delete()

@integration_test
class TestAddUpdateKubeUsingIO(unittest.TestCase):
    def test_add_by_string_io(self):
        """adds the CSV file using stringIO object"""
        input = requests.get(URL).text
        input_io = io.StringIO(input)
        data = pd.read_csv(input_io)
        output = io.StringIO()
        data.to_csv(output, index=False)
        gis = GIS(
            profile=PROFILES[1],
            verify_cert=False,
            trust_env=True,
        )
        item = None
        try:
            item = gis.content.add(item_properties, data=output)
            assert item
        except Exception as e:
            raise e
        finally:
            if item:
                item.delete()

    def test_update_by_string_io(self):
        """adds the CSV file using stringIO object"""
        input = requests.get(URL).text
        input_io = io.StringIO(input)
        data = pd.read_csv(input_io)
        output = io.StringIO()
        data.to_csv(output, index=False)
        gis = GIS(
            profile=PROFILES[1],
            verify_cert=False,
            trust_env=True,
        )
        item = gis.content.add(item_properties, data=output)
        assert item
        try:
            assert item.update(data=output)
        except Exception as e:
            raise e
        finally:
            if item:
                assert item.delete()


if __name__ == "__main__":
    unittest.main()
