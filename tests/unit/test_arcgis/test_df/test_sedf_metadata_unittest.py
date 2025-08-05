import unittest
from arcgis.features.geo._tools._metadata import _Metadata
from arcgis._impl.common._isd import InsensitiveDict

class TestMetadata(unittest.TestCase):
    def setUp(self):
        self.meta = _Metadata()

    def test_source_property(self):
        dummy_source = object()
        self.meta.source = dummy_source
        self.assertIs(self.meta.source, dummy_source)

    def test_geometry_type_property(self):
        self.meta.geometry_type = "Polygon"
        self.assertEqual(self.meta.geometry_type, "Polygon")

    def test_renderer_setter_with_dict(self):
        renderer_dict = {"type": "simple", "symbol": {"type": "esriSMS"}}
        self.meta.renderer = renderer_dict
        self.assertIsInstance(self.meta.renderer, InsensitiveDict)
        self.assertEqual(self.meta.renderer["type"], "simple")

    def test_renderer_setter_with_insensitivedict(self):
        renderer_idict = InsensitiveDict.from_dict({"type": "uniqueValue"})
        self.meta.renderer = renderer_idict
        self.assertIs(self.meta.renderer, renderer_idict)

    def test_renderer_setter_with_invalid_type(self):
        with self.assertRaises(ValueError):
            self.meta.renderer = [1, 2, 3]

    def test_source_type(self):
        class DummySource: pass
        dummy = DummySource()
        self.meta.source = dummy
        self.assertEqual(self.meta.source_type, "DummySource")
        self.meta.source = None
        self.assertIsNone(self.meta.source_type)

    def test_str_and_repr(self):
        s = str(self.meta)
        r = repr(self.meta)
        self.assertIn("_Metadata", s)
        self.assertIn("_Metadata", r)

    def test_pickle_support(self):
        state = {"_source": 1, "_renderer": 2, "_geometry_type": "Point"}
        self.meta.__setstate__(state)
        self.assertEqual(self.meta._source, 1)
        self.assertEqual(self.meta._renderer, 2)
        self.assertEqual(self.meta._geometry_type, "Point")
        self.assertEqual(self.meta.__getstate__(), self.meta.__dict__)

if __name__ == "__main__":
    unittest.main()
