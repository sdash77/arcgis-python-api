from arcgis.gis import Item
class PlaceholderItem(Item):
    type = "unspecified"
    id = "958e44bf8fb943d68b783a9f5f6b17ee"
    url = "https://example.com"
    def __init__(self, *args, **kwargs):
        pass
    def __getattr__(self, *args, **kwargs):
        try:
            return dict.__getitem__(self, *args, **kwargs)
        except Exception as e:
            raise AttributeError