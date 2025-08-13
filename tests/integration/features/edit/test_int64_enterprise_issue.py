import unittest

import pandas as pd
from arcgis.geometry import Geometry
from config import get_json_resource
from utils.decorators import integration_test, profiles
from ._shared_data import get_edit_features_test_data


@profiles.all
@integration_test
class TestIssueInt64(unittest.TestCase):
    """tests the fact that int64 is only accepted on Online(November2023) and Enterprise 11.2+"""

    def test_create_sdf_with_int64(self):
        """Create a spatially enabled dataframe and publish an item with it to different portals."""
        item = None
        try:
            test_data = get_edit_features_test_data(self.gis)
            sdf = pd.DataFrame(test_data)
            sdf.SHAPE = sdf.SHAPE.apply(lambda x: Geometry(x))
            sdf.spatial.set_geometry("SHAPE")
            assert not sdf.empty

            item = self.gis.content.import_data(sdf, tags="ntgrtn-tst")
            assert item
        except Exception as e:
            self.fail(e)
        finally:
            if item:
                item.delete(permanent=True)

    @classmethod
    def generate_test_data(cls):
        test_data = get_json_resource("features/edit.json")
        if cls.gis._is_arcgisonline:
            # datetime offset not supported in hosted enterprise FLs
            # test using DateTimeOffset with AGOL
            for feature in test_data:
                if "ts" in feature:
                    feature["ts"] = Timestamp(feature["ts"])

        return test_data


if __name__ == "__main__":
    unittest.main()
