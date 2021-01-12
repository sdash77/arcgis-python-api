from unittest.mock import MagicMock
try:
    from arcgis.features import FeatureLayerCollection
except Exception:
    class FeatureLayerCollection:
        pass

class PlaceholderFeatureLayerCollection(FeatureLayerCollection):
    def __init__(self, *args, **kwargs):
        pass
    url = "https://example.com"
    properties = MagicMock()
    layers = []
    tables = []