import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import unittest
import pandas as pd
import os, shutil
try:
    import arcpy
    HAS_ARCPY = True
except:
    HAS_ARCPY = False
"""
ServiceFactory Tests
"""
import os
import arcgis
from arcgis.gis.server._service._layerfactory import Service
from arcgis.features.layer import Layer#
from arcgis.features.layer import FeatureLayer, FeatureLayerCollection#
from arcgis.geocoding import Geocoder#
from arcgis.geoprocessing._tool import Toolbox#
from arcgis._impl.tools import _GeometryService as GeometryService#
from arcgis.network import NetworkDataset#
from arcgis.mapping import VectorTileLayer
from arcgis.mapping import MapImageLayer#
from arcgis.raster import ImageryLayer#
from arcgis.schematics import SchematicLayers
from arcgis.mapping._types import SceneLayer
############################################################################
#@unittest.SkipTest
class ServiceFactoryTest(unittest.TestCase):
    """test ServiceFactory Class"""
    def test_mobile(self):
        url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/WindTurbines/MobileServer"
        service = Service(url=url)
        self.assertIsInstance(service, Layer)
    def test_gp(self):
        url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/GPServer"
        service = Service(url=url)
        self.assertIsInstance(service, Toolbox)
        from arcgis.gis import GIS
        gis = GIS("https://deldev.maps.arcgis.com", "demos_deldev", "DelDevs12", verify_cert=False)
        service = Service(url=url)
        #assert service.execute_911_calls_hotspot()
        self.assertIsInstance(service, Toolbox)
    def test_fs(self):
        url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/CommercialDamageAssessment/FeatureServer"
        service = Service(url=url)
        self.assertIsInstance(service, FeatureLayerCollection)
    def test_fl(self):
        url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/CommercialDamageAssessment/FeatureServer/0"
        service = Service(url=url)
        self.assertIsInstance(service, FeatureLayer)
    def test_mapservice(self):
        url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/MapServer"
        service = Service(url=url)
        self.assertIsInstance(service, MapImageLayer)
    def test_geocoder(self):
        url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Locators/Composite_HBR_Asset/GeocodeServer"
        service = Service(url=url)
        self.assertIsInstance(service, Geocoder)
    def test_geometry(self):
        url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Utilities/Geometry/GeometryServer"
        service = Service(url=url)
        self.assertIsInstance(service, GeometryService)
    def test_imageservice(self):
        url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/ScientificData/MODIS_Landcover/ImageServer"
        service = Service(url=url)
        self.assertIsInstance(service, ImageryLayer)
    def test_NA(self):
        url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/NetworkAnalysis/SanDiego/NAServer"
        service = Service(url=url)
        self.assertIsInstance(service, NetworkDataset)
    ##TODO: FIND PUBLIC SCENE, VECTOR AND SCHEMATIC SERVICE ENDPOINTS
#--------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()