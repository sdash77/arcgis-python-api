# Placeholders aren't exactly mocks -- they're 'placeholder' classes that
# inherit from real `arcgis` classes but have all their main functionality
# removed so you can hit the correct areas of code for testing other classes

from utils.mocks.placeholders.placeholder_item import PlaceholderItem
from utils.mocks.placeholders.placeholder_featurelayer import PlaceholderFeatureLayer
from utils.mocks.placeholders.placeholder_featurelayercollection import PlaceholderFeatureLayerCollection
from utils.mocks.placeholders.placeholder_table import PlaceholderTable