# -------------------------------------------------------------------------------
# Name:        CertificateManager class tests
# Purpose:     Sanity tests for ArcGIS Python API
# -------------------------------------------------------------------------------
import unittest
from pathlib import Path
from utils.decorators import integration_test


@integration_test
class TestCertificateMgr(unittest.TestCase):
    def test_certificate_manager(self):
        from arcgis.gis import GIS

        profiles = ["your_online_admin_profile"]
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False)
            assert gis.admin.certificates
            cm = gis.admin.certificates
            assert cm.properties
            assert isinstance(gis.admin.certificates.certificates, (list, tuple))
            data_dir = Path(Path.cwd(), "integration", "gis", "admin", "cert_test.txt")
            with open(data_dir) as reader:
                result = cm.add(
                    name="MYSELFSIGNEDCERT",
                    domain="esri.com",
                    certificate=reader.read(),
                )
                assert result
                for c in [
                    cert["id"]
                    for cert in cm.certificates
                    if cert["name"] == "MYSELFSIGNEDCERT"
                ]:
                    g = cm.get(c)
                    assert g
                    assert g["name"] == "MYSELFSIGNEDCERT"
                    assert cm.update(c, name="foodbar")
                    g = cm.get(c)
                    assert g
                    assert g["name"] == "foodbar"
                    assert cm.delete(c)
            [
                cm.delete(c["id"])
                for c in cm.certificates
                if c["name"] in ["foodbar", "MYSELFSIGNEDCERT"]
            ]  # CLEAN UP SCRIPT


if __name__ == "__main__":
    unittest.main()
