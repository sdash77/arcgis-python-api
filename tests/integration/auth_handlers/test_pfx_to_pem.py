import os
import unittest
import arcgis.auth

from utils.decorators import integration_test


@integration_test
class TestCertificateTools(unittest.TestCase):
    def test_pfx_to_pem(self):
        current_folder = os.path.dirname(os.path.realpath(__file__))
        cert_file, private_key_file = arcgis.auth.tools.pfx_to_pem(
            pfx_path=f"{current_folder}/sample.pfx", pfx_password="portalaccount1"
        )
        assert os.path.isfile(private_key_file)
        with open(private_key_file, "r") as f:
            private_key = f.read()
        assert "BEGIN PRIVATE KEY" in private_key
        assert "END PRIVATE KEY" in private_key
        assert os.path.isfile(cert_file)
        with open(cert_file, "r") as f:
            cert = f.read()
        assert "BEGIN CERTIFICATE" in cert
        assert "END CERTIFICATE" in cert


if __name__ == "__main__":
    unittest.main()
