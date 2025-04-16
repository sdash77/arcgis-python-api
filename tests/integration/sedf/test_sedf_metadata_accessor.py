"""
Tests for the private GeoAccessor `_Metadata` Class.

This class holds the source information inside a spatially enabled dataframe. 
"""

import os
import tempfile
import unittest

from arcgis._impl.common._isd import InsensitiveDict
from arcgis.features.geo._tools._metadata import _Metadata
from utils.decorators import integration_test


###########################################################################
@integration_test
class TestMetaDataClass(unittest.TestCase):
    """Tests the Private _Metadata Class"""

    def test_init(self):
        """asserts that the object can be initialized"""
        m = _Metadata()
        assert isinstance(m, _Metadata)

    def test_str(self):
        """tests the __str__"""
        assert str(_Metadata()) == "<_Metadata>"

    def test_repr(self):
        """tests the __repr__"""
        assert _Metadata().__repr__() == "<_Metadata>"

    def test_get_set_source(self):
        """tests the get/set source property"""
        m = _Metadata()
        m.source = "foo"
        assert m.source == "foo"

    def test_source_type(self):
        """tests the property for the source type"""
        from arcgis.features import FeatureLayer

        m = _Metadata()
        assert m.source_type is None
        m.source = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"
        )
        assert isinstance(m.source_type, str)
        assert m.source_type == "FeatureLayer"

    def test_pickle(self):
        """tests pickling the _Metadata Class"""
        m = _Metadata()
        m.source = "pickle"
        m.renderer = {"pickle": "me"}
        import pickle

        o = pickle.dumps(m)
        assert isinstance(o, (bytes, bytearray))
        m2 = pickle.loads(o)
        assert m.source == m2.source
        assert m.renderer == m2.renderer

    def test_get_set_renderer(self):
        """tests get/set the renderer from a PropertyMap, Dict, and InsensitiveDict"""
        from arcgis.features import FeatureLayer

        m = _Metadata()
        fl = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"
        )
        r_property = fl.properties.drawingInfo.renderer
        r_dict = dict(r_property)
        r_isd = InsensitiveDict(r_dict)
        for r in [r_dict, r_property, r_isd]:
            m.renderer = r
            assert m.renderer
            assert isinstance(m.renderer, InsensitiveDict)


###########################################################################
@integration_test
class TestAttrSeDFMetadata(unittest.TestCase):
    """tests the functionality of the _Metadata class on SeDF"""

    def test_metadata_on_sedf(self):
        """tests the hidden _meta property on the SeDF"""
        from arcgis.features import FeatureLayer

        fl = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"
        )
        sdf = fl.query(as_df=True)
        print(sdf)
        assert sdf.spatial._meta
        assert isinstance(sdf.spatial._meta.renderer, InsensitiveDict)
        assert isinstance(sdf.spatial._meta.source, (FeatureLayer, str))
        assert isinstance(sdf.spatial._meta.source_type, str)
        assert sdf.spatial._meta.source_type == "str"

    def test_pickle_on_sedf(self):
        """tests the hidden _meta property with to/from pickle operations"""
        from arcgis.features import FeatureLayer
        import pandas as pd

        fl = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"
        )
        sdf = fl.query(as_df=True)
        assert sdf.spatial._meta
        assert isinstance(sdf.spatial._meta.renderer, InsensitiveDict)
        assert isinstance(sdf.spatial._meta.source, str)
        assert isinstance(sdf.spatial._meta.source_type, str)
        assert sdf.spatial._meta.source_type == "str"
        with tempfile.TemporaryDirectory() as tmpdirname:
            fp = os.path.join(tmpdirname, "test.pickle")
            sdf.to_pickle(fp)
            sdf2 = pd.read_pickle(fp)
            assert sdf2.spatial._meta
            assert isinstance(sdf2.spatial._meta.renderer, InsensitiveDict)
            assert isinstance(sdf2.spatial._meta.source, str)
            assert isinstance(sdf2.spatial._meta.source_type, str)
            assert sdf2.spatial._meta.source_type == "str"
            os.remove(fp)


if __name__ == "__main__":
    unittest.main()
