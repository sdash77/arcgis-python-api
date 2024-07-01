"""
The arcgis.layers module provides components for visualizing GIS data and analysis.
This module also includes mapping layers like MapImageLayer, SceneLayer and VectorTileLayer.
"""

from ._vtl._vector_tile_layers import (
    VectorTileLayer,
    VectorTileLayerManager,
    EnterpriseVectorTileLayerManager,
)

from arcgis.layers._scenelyrs import (
    Object3DLayer,
    IntegratedMeshLayer,
    Tiles3DLayer,
    Point3DLayer,
    VoxelLayer,
)
from arcgis.layers._scenelyrs import PointCloudLayer, BuildingLayer, SceneLayer
from arcgis.layers._scenelyrs import (
    SceneLayerManager,
    EnterpriseSceneLayerManager,
)
from arcgis.layers._msl import (
    MapServiceLayer,
    MapFeatureLayer,
    MapTable,
    MapRasterLayer,
    MapImageLayer,
    MapImageLayerManager,
    EnterpriseMapImageLayerManager,
)
from ._ogc._wms import WMSLayer
from ._ogc.wmts import WMTSLayer
from ._ogc._csv import CSVLayer
from ._ogc._georss import GeoRSSLayer
from ._ogc._kml import KMLLayer
from ._ogc._geojson import GeoJSONLayer
from ._ogc._service import OGCCollection, OGCFeatureService

from ._service_factory._layerfactory import Service, ServiceFactory

__all__ = [
    "MapImageLayer",
    "MapImageLayerManager",
    "EnterpriseMapImageLayerManager",
    "VectorTileLayer",
    "VectorTileLayerManager",
    "EnterpriseVectorTileLayerManager",
    "get_layout_templates",
    "OfflineMapAreaManager",
    "SceneLayer",
    "SceneLayerManager",
    "EnterpriseSceneLayerManager",
    "Object3DLayer",
    "IntegratedMeshLayer",
    "Tiles3DLayer",
    "Point3DLayer",
    "PointCloudLayer",
    "BuildingLayer",
    "VoxelLayer",
    "MapServiceLayer",
    "MapFeatureLayer",
    "MapTable",
    "MapRasterLayer",
    "WMSLayer",
    "WMTSLayer",
    "CSVLayer",
    "GeoRSSLayer",
    "KMLLayer",
    "GeoJSONLayer",
    "OGCCollection",
    "OGCFeatureService",
    "Service",
    "ServiceFactory",
]
