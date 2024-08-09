from arcgis.map import Map
import unittest
from utils.decorators import integration_test, profiles


@profiles.agol
@integration_test
class TestBookmarksMap(unittest.TestCase):
    def test_bookmarks(self):
        """Test getting, adding, and deleting bookmarks"""

        webmap = Map(gis=self.gis)
        assert webmap

        bookmarks = webmap.bookmarks
        assert bookmarks
        bookmarks.add(
            name="Bookmark1",
            extent={
                "xmin": -13458971.714869041,
                "ymin": 3612376.446092521,
                "xmax": -12305256.512287628,
                "ymax": 4354833.185272345,
                "spatialReference": {"wkid": 102100},
            },
            rotation=0,
        )
        assert len(bookmarks.list) == 1

        bookmarks.remove(0)
        assert len(bookmarks.list) == 0


if __name__ == "__main__":
    unittest.main()
