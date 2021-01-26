from unittest.mock import MagicMock
try:
    from arcgis.features import FeatureLayer
except Exception:
    class FeatureLayer:
        pass

class PlaceholderFeatureLayer(FeatureLayer):
    def __init__(self, *args, **kwargs):
        pass
    url = "https://example.com"
    properties = MagicMock()
    _extent = {}