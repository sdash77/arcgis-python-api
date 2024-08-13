import time
import unittest
from arcgis.features.layer import FeatureLayerCollection
from arcgis.gis import GIS
from tests.integration.parcels import parcel_fabric_utils as pfutils
from utils.decorators import integration_test

@integration_test
class TestVersionManagementSQL(unittest.TestCase):
    """Test VersionManagementServer methods"""

    record_name = None
    records_fl = None
    timestamp = None
    vms = None
    gis = None
    services = None
    service_urls = {}
    version_name = None
    base_server_url = None
    parcel_fabric_flc = None

    @classmethod
    def setUpClass(cls):
        # Create Python API GIS object and prepare REST service URL strings
        cls.base_server_url = (
            "https://dev0016752.esri.com/server/rest/services/WashingtonCountyLSA/"
        )
        cls.gis = GIS(
            "https://dev0016752.esri.com/portal/",
            "admin",
            "esri.agp",
            verify_cert=False,
        )
        endpoints = ["FeatureServer", "ParcelFabricServer", "VersionManagementServer"]
        cls.service_urls = {url: cls.base_server_url + url for url in endpoints}
        cls.parcel_fabric_flc = FeatureLayerCollection(
            cls.service_urls["FeatureServer"], cls.gis
        )
        cls.vms = cls.parcel_fabric_flc.versions
        cls.records_fl = pfutils.get_feature_layer(
            cls.parcel_fabric_flc, "Records"
        )

        cls.timestamp = int(time.time())
        cls.record_name = f"api-{cls.timestamp}"

    def test_is_edit_lock_removed(self):
        _version_name_txt = "api-{}".format(int(time.time()))
        self.vms.create(_version_name_txt)
        fq_version_name = f"admin.{_version_name_txt}"

        with self.vms.get(fq_version_name, "edit") as version:
            # start the 'edit' session
            self.assertTrue(version.properties.isBeingRead, "Read session not open")
            self.assertTrue(version.properties.isBeingEdited, "Edit session not open")

        # Outside of with statement
        self.assertFalse(version.properties.isBeingRead, "Read session still open")
        self.assertFalse(version.properties.isBeingEdited, "Edit session still open")

    def test_is_read_lock_removed(self):
        _version_name_txt = "api-{}".format(int(time.time()))
        self.vms.create(_version_name_txt)
        fq_version_name = f"admin.{_version_name_txt}"

        with self.vms.get(fq_version_name, "read") as version:
            # start the 'edit' session
            self.assertTrue(version.properties.isBeingRead, "Read session not open")

        # Outside of with statement
        self.assertFalse(version.properties.isBeingRead, "Read session still open")
        self.assertFalse(version.properties.isBeingEdited, "Edit session still open")

    def test_read_set_mode_to_edit(self):
        """Enter 'read' mode then set the mode property to 'edit'
        Should have read and edit locks within the context manager
        Exiting the context manager should find the locks removed
        """
        _version_name_txt = "api-{}".format(int(time.time()))
        self.vms.create(_version_name_txt)
        fq_version_name = f"admin.{_version_name_txt}"

        with self.vms.get(fq_version_name, "read") as version:
            # start the 'edit' session
            version.mode = "edit"
            self.assertTrue(version.properties.isBeingEdited, "Edit session not open")

        # Outside of with statement
        self.assertFalse(version.properties.isBeingRead, "Read session still open")
        self.assertFalse(version.properties.isBeingEdited, "Edit session still open")
        self.assertFalse(version.properties.isLocked, "The version is still locked")

    def test_edit_set_mode_to_read(self):
        """Enter 'edit' mode then set the mode property to 'read'
        Should have read and edit locks within the context manager
        Exiting the context manager should find the locks removed
        """
        _version_name_txt = "api-{}".format(int(time.time()))
        self.vms.create(_version_name_txt)
        fq_version_name = f"admin.{_version_name_txt}"

        with self.vms.get(fq_version_name, "read") as version:
            # start the 'edit' session
            version.mode = "edit"
            # self.assertTrue(version.properties.isBeingEdited, "Edit session not open")

        # Outside of with statement
        self.assertFalse(version.properties.isBeingRead, "Read session still open")
        self.assertFalse(version.properties.isBeingEdited, "Edit session still open")
        self.assertFalse(version.properties.isLocked, "The version is still locked")

    def test_manually_set_editing_modes(self):
        """Set each mode 'read', 'edit', 'none' and check status.
        If locks cleared properly, should be able to delete the version"""
        # Create a new version
        _version_name_txt = "api-{}".format(int(time.time()))
        self.vms.create(_version_name_txt)
        fq_version_name = f"admin.{_version_name_txt}"

        version = self.vms.get(fq_version_name, None)
        self.assertIsNotNone(version, "Error getting new version object")

        version.mode = "read"
        self.assertTrue(version.properties.isBeingRead, "isBeingRead not set")
        self.assertTrue(version.properties.isLocked, "The version is not locked")

        version.mode = "edit"
        self.assertTrue(version.properties.isBeingEdited, "isBeingEdited not set")
        self.assertTrue(version.properties.isLocked, "The version is not locked")
        self.assertTrue(version.properties.isBeingEdited, "isBeingEdited not set")

        version.mode = None
        self.assertFalse(version.properties.isBeingEdited, "Version still in edit mode")
        self.assertFalse(version.properties.isBeingRead, "Version still in read mode")

        deleted_version = version.delete()
        self.assertTrue(deleted_version, "The version was not deleted.")


if __name__ == "__main__":
    unittest.main()
