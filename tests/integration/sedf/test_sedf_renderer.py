import os
import tempfile
import unittest

import pandas as pd
from arcgis._impl.common._isd import InsensitiveDict
from utils.decorators import integration_test


@integration_test
class TestSeDFRenderer(unittest.TestCase):
    """tests the visualizer on the SeDF"""

    def test_from_feature_layer(self):
        """tests pulling in the renderer from the FeatureLayer"""
        from arcgis.features import FeatureLayer

        fl = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"
        )
        sdf = fl.query(as_df=True)
        assert sdf.spatial.renderer == InsensitiveDict(
            fl.properties.drawingInfo.renderer
        )

    def test_self_created(self):
        """tests the case when a SeDF is created manually"""
        from arcgis.geometry import Geometry

        geoms = [
            Geometry({"x": -118.15, "y": 33.80, "spatialReference": {"wkid": 4326}})
        ] * 5
        data = {"SHAPE": geoms, "L1": [1, 2, 3, 4, 5]}
        df = pd.DataFrame(data=data)

        assert df.spatial._meta
        assert df.spatial.renderer
        assert df.spatial._meta
        assert df.spatial._meta.source_type is None
        assert df.spatial._meta.source is None

    def test_from_feature_class(self):
        """tests shows that feature classes get assigned a default symbology and it should not equal the feature layer"""
        from arcgis.features import FeatureLayer

        fl = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"
        )
        sdf = fl.query(as_df=True)
        temp_dir = tempfile.mkdtemp()
        fp = os.path.join(temp_dir, "states.shp")
        data = sdf.spatial.to_featureclass(fp)
        sdf2 = pd.DataFrame.spatial.from_featureclass(data)
        assert sdf2.spatial.renderer != InsensitiveDict(
            fl.properties.drawingInfo.renderer
        )
        assert sdf2.spatial._meta
        assert sdf2.spatial._meta.renderer
        assert sdf2.spatial._meta.source
        assert sdf2.spatial._meta.source_type


if __name__ == "__main__":
    unittest.main()
