import unittest
from arcgis.auth import EsriUserTokenAuth

class TestUserToken(unittest.TestCase):
    def test_with_no_token(self):
        with self.assertRaises(ValueError):
            EsriUserTokenAuth(
                token=None, referer=None, verify_cert=True, legacy=False
            )

    def test_referer_set(self):
        token_auth = EsriUserTokenAuth(
            token="ABCD", referer="ABCD", verify_cert=True, legacy=False
        )
        assert token_auth.referer == "ABCD"

if __name__ == "__main__":
    unittest.main()