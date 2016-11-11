"""
The arcgis.mapping module provides components for visualizing GIS data and analysis.
This module includes components such as MapView - an IPython Notebook widget for
working with maps, as well as WebMap and WebScene components that enable 2D and 3D
mapping and visualization in the GIS. This module also includes mapping layers like
DynamicMapLayer and VectorTileLayer
"""

from .types import WebMap, WebScene, MapView, MapImageLayer, MapImageLayerManager, VectorTileLayer

__all__ = ['WebMap', 'WebScene', 'MapView', 'MapImageLayer', 'MapImageLayerManager', 'VectorTileLayer']
