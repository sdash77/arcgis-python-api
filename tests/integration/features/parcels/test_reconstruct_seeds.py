"""
Test class for parcel fabric's Reconstruct From Seeds
"""

import json
import unittest
import time

from arcgis.gis import GIS
from arcgis.features.layer import FeatureLayerCollection, FeatureSet
from arcgis.features._parcel import ParcelFabricManager

from utils.decorators import integration_test, profiles
from . import parcel_fabric_utils as pfutils


@profiles.parcel_fabric
@integration_test
class TestShrinkReconstructSeeds(unittest.TestCase):
    gis = None
    vms = None
    services = None
    service_urls = {}
    base_server_url = None
    parcel_fabric_flc = None

    @classmethod
    def setUpClass(cls):
        # Create Python API GIS object and prepare REST service URL strings
        cls.base_server_url = (
            "https://dev0016752.esri.com/server/rest/services/HCAD_Subset/"
        )

        endpoints = ["FeatureServer", "ParcelFabricServer", "VersionManagementServer"]
        cls.service_urls = {url: cls.base_server_url + url for url in endpoints}
        cls.parcel_fabric_flc = FeatureLayerCollection(
            cls.service_urls["FeatureServer"], cls.gis
        )
        cls.vms = cls.parcel_fabric_flc.versions
        cls.edit_version = cls.vms.create(f"api-{int(time.time())}")

    def test_ShrinkToSeedsThenReconstruct(self):
        """
        Shrink some parcels to seeds (applyEdits) then use reconstruct_from_seeds to build them
        """
        fq_version_name = self.edit_version["versionInfo"]["versionName"]
        extent = self.get_aoi_extent()
        ids_to_shrink = [181, 256, 345178, 258, 259]
        where = pfutils._generate_where_in_clause("OBJECTID", ids_to_shrink)

        parcels_fl = pfutils.get_feature_layer(self.parcel_fabric_flc, "Tax")
        parcel_features = parcels_fl.query(where=where).features
        for f in parcel_features:
            f.attributes["IsSeed"] = 1

        shrink_to_seeds = parcels_fl.edit_features(
            updates=parcel_features, gdb_version=fq_version_name
        )
        self.assertEqual(
            5, len(shrink_to_seeds["updateResults"]), "Incorrect update count"
        )

        is_seed = pfutils.query_service(
            self.service_urls["FeatureServer"],
            self.gis,
            fl_id=15,
            out_fields=["OBJECTID"],
            where="IsSeed = 1",
            version_name=fq_version_name,
        )
        self.assertEqual(5, len(is_seed))

        with self.vms.get(fq_version_name, "read") as version:
            parcel_fabric = ParcelFabricManager(
                self.service_urls["ParcelFabricServer"],
                self.gis,
                version,
                self.parcel_fabric_flc,
            )
            rcfs = parcel_fabric.reconstruct_from_seeds(extent=extent)
        self.assertIsNotNone(rcfs["serviceEdits"], "Empty serviceEdits list")
        self.assertEqual(
            5,
            rcfs["reconstructedParcelCount"],
            "Incorrect reconstructedParcelCount value",
        )

    @classmethod
    def get_aoi_extent(cls):
        extent_str = """{"xmin":3157152.13081438188,
                         "ymin":13845980.1254367381,
                         "xmax":3160282.1149064675,
                         "ymax":13848182.5011111163,
                         "spatialReference":
                            {"wkid":102740,
                             "latestWkid":2278}}
                        """
        return json.loads(extent_str)

    @classmethod
    def tearDownClass(cls):
        pfutils.clean_up_versions(cls.vms)


if __name__ == "__main__":
    unittest.main()
