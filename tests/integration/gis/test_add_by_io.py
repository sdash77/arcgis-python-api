import unittest
import io
import sys
import uuid

sys.path.insert(0, r"C:\SVN\geosaurus_master_issue_6198\src")

from arcgis.gis import GIS
import pandas as pd

GUID = uuid.uuid4().hex[:6]
item_properties = {
    "type": "CSV",
    "title": f"IOTest{GUID}",
    "fileName": f"io_{GUID}_test.csv",
}
URL = (
    "https://raw.githubusercontent.com/jbrownlee/Datasets/master/airline-passengers.csv"
)
PROFILE = "your_online_profile"


class TestAddUsingIO(unittest.TestCase):
    def test_add_by_string_io(self):
        """adds the CSV file using stringIO object"""
        data = pd.read_csv(URL)
        output = io.StringIO()
        data.to_csv(output, index=False)
        gis = GIS(profile=PROFILE, verify_cert=False, trust_env=True)
        item = gis.content.add(item_properties, data=output)
        assert item
        assert item.delete()


if __name__ == "__main__":
    unittest.main()
