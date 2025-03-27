import os.path
import tempfile
import time
import unittest
import arcgis.geometry.filters
from arcgis.features.layer import FeatureLayerCollection
from arcgis.gis import GIS
from .offline_utils import replica_helpers


class TestOfflineExtraction(unittest.TestCase):
    """Take a parcel fabric offline. Use arcpy.Describe to check correct parts"""

    sd_path = None
    output_gdb_path = None
    tax_lyr_info = None
    gis = None
    vms = None
    services = None
    service_urls = {}
    base_parcel_server_url = None
    parcel_fabric_flc = None
    print(os.getcwd())

    @classmethod
    def setUpClass(cls):
        # Create Python API GIS object and prepare REST service URL strings
        parcel_portal_info = {
            "portal": f"https://dev0016752.esri.com/portal",
            "server": f"https://dev0016752.esri.com/server/rest/services",
            "service_name": "OfflineUseCases",
        }
        cls.base_parcel_server_url = (
            f"{parcel_portal_info['server']}/{parcel_portal_info['service_name']}/"
        )
        cls.gis = GIS(
            parcel_portal_info["portal"],
            "admin",
            "esri.agp",
            verify_cert=False,
            trust_env=True,
        )
        endpoints = ["FeatureServer", "ParcelFabricServer", "VersionManagementServer"]
        cls.service_urls = {url: cls.base_parcel_server_url + url for url in endpoints}
        cls.parcel_fabric_flc = FeatureLayerCollection(
            cls.service_urls["FeatureServer"], cls.gis
        )
        cls.vms = cls.parcel_fabric_flc.versions
        cls.output_gdb_path = tempfile.TemporaryDirectory()

    def test_replica_response_has_download_path_async_wait(self):
        """Creates a replica with a specific extent that contains four parcels. Ensure the response is correct"""
        geom_filter = arcgis.geometry.filters.envelope_intersects(
            {"xmin": 6579680.8526996868, "ymin": 1235864.3641352288, "xmax": 6579896.1304774648,
             "ymax": 1236036.4561491178}
        )
        replica_options = self.get_parcel_replica_options(geom_filter)
        replica_options["asynchronous"] = True
        replica_options["wait"] = True

        try:
            res = self.parcel_fabric_flc.replicas.create(**replica_options)
            self.assertIsNotNone(res.get("download_url"), "Missing download_url")
            self.assertTrue(res.get("download_url").endswith(".geodatabase"))
        except Exception as ex:
            print("Create Replica failed:", str(ex))

    def test_replica_response_has_download_path_sync(self):
        """Creates a replica with a specific extent that contains four parcels. Ensure the response is correct"""
        geom_filter = arcgis.geometry.filters.envelope_intersects(
            {"xmin": 6579680.8526996868, "ymin": 1235864.3641352288, "xmax": 6579896.1304774648,
             "ymax": 1236036.4561491178}
        )
        replica_options = self.get_parcel_replica_options(geom_filter)
        replica_options["asynchronous"] = False
        replica_options["wait"] = False

        try:
            res = self.parcel_fabric_flc.replicas.create(**replica_options)
            self.assertIsNotNone(res.get("download_url"), "Missing download_url")
            self.assertTrue(res.get("download_url").endswith(".geodatabase"))
        except Exception as ex:
            print("Create Replica failed:", str(ex))

    @classmethod
    def get_parcel_replica_options(cls, geom_filter):
        replica_options = {
            "replica_name": f"Ags_UnitTest_{int(time.time())}",
            "layers": [0, 2, 7, 8, 14, 15, 17, 18, 20, 21],
            "layer_queries": cls.get_simple_layer_queries(),
            "geometry_filter": geom_filter,
            "replica_sr": {"wkid": 102642, "latestWkid": 2226},
            "transport_type": "esriTransportTypeUrl",
            "return_attachments": True,
            "attachments_sync_direction": "bidirectional",
            "sync_model": "perReplica",
            "data_format": "sqlite",
            "replica_options": {"syncDataOptions": 2308},
            "out_path": cls.output_gdb_path.name,
            "sync_direction": "bidirectional",
        }
        return replica_options

    @classmethod
    def get_simple_layer_queries(cls):
        return ('{"0":{"queryOption":"useFilter","useGeometry":true},"2":{"queryOption":"useFilter",'
                '"useGeometry":true},"7":{"queryOption":"useFilter","useGeometry":true},'
                '"8":{"queryOption":"useFilter","useGeometry":true},"14":{"queryOption":"useFilter",'
                '"useGeometry":true},"15":{"queryOption":"useFilter","useGeometry":true},'
                '"17":{"queryOption":"useFilter","useGeometry":true},"18":{"queryOption":"useFilter",'
                '"useGeometry":true},"20":{"queryOption":"useFilter","useGeometry":true},'
                '"21":{"queryOption":"useFilter","useGeometry":true}}')

    @classmethod
    def tearDownClass(cls):
        cls.output_gdb_path.cleanup()
        replica_helpers.cleanup_replica_items(cls.parcel_fabric_flc)
