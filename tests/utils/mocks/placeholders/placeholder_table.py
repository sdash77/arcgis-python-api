from unittest.mock import MagicMock
try:
    from arcgis.features import Table
except Exception:
    class Table:
        pass

class PlaceholderTable(Table):
    def __init__(self, *args, **kwargs):
        self.properties = MagicMock()
        self.properties.name = "Example Table"
        self.properties.serviceItemId = "3a75424edd645e8e0b8d3860a8530525"
        pass
    url = "https://example.com"
    properties = MagicMock()