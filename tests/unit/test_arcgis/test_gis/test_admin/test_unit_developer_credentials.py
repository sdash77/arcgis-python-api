import unittest
from unittest.mock import MagicMock, patch

from arcgis.gis.admin._stokenmgr import (
    TokenPrivilege,
    DeveloperCredential,
    DeveloperCredentialManager,
)

class DummyItem:
    def __init__(self):
        self._gis = MagicMock()
        self._gis.session = MagicMock()
        self.id = "abc123"
        self.itemid = "abc123"
        self.type = "Application"
        self.typeKeywords = ["APIToken"]
        self.app_info = {
            "client_id": "cid",
            "client_secret": "csecret",
            "httpReferrers": [],
            "privileges": [],
        }
    def delete(self, permanent=False):
        return permanent
    def update(self, *args, **kwargs):
        return True
    def register(self, *args, **kwargs):
        return MagicMock()
    def __getattr__(self, name):
        return MagicMock()

class DummyGIS:
    def __init__(self):
        self.url = "https://example.com"
        self.session = MagicMock()
        self.version = [2025, 1]
        self._is_arcgisonline = True
        self.content = MagicMock()
        self.content.folders = MagicMock()
        self.content.folders.get = MagicMock(return_value=MagicMock())
        self.content.get = MagicMock(return_value=DummyItem())
        self.content.advanced_search = MagicMock(return_value={"results": [DummyItem()]})
        self.users = MagicMock()
        self.users.me = MagicMock(username="testuser")

class TestTokenPrivilege(unittest.TestCase):
    def test_enum_values(self):
        self.assertEqual(TokenPrivilege.PORTAL_USER_VIEWORGUSERS.value, "portal:user:viewOrgUsers")
        self.assertIsInstance(TokenPrivilege.PREMIUM_USER_GEOENRICHMENT.value, str)

class TestDeveloperCredential(unittest.TestCase):
    def setUp(self):
        self.dummy_item = DummyItem()

    def test_init(self):
        cred = DeveloperCredential(self.dummy_item)
        self.assertEqual(cred._item, self.dummy_item)
        self.assertEqual(cred._gis, self.dummy_item._gis)

    def test_session_property(self):
        cred = DeveloperCredential(self.dummy_item)
        cred._session = self.dummy_item._gis.session
        self.assertEqual(cred.session, self.dummy_item._gis.session)

    def test_str_repr(self):
        cred = DeveloperCredential(self.dummy_item)
        self.assertIn("Item ID", str(cred))
        self.assertIn("Item ID", repr(cred))

    def test_delete(self):
        cred = DeveloperCredential(self.dummy_item)
        self.assertTrue(cred.delete())
        cred._item = None
        self.assertFalse(cred.delete())

    def test_update(self):
        cred = DeveloperCredential(self.dummy_item)
        
        cred.session.post.return_value = MagicMock(
            json=lambda: {"apiToken1Active": False, "apiToken2Active": False},
            raise_for_status=lambda: None,
        )
        self.assertFalse(cred.update())
        self.assertTrue(cred.update(redirect_uris=["a"], referers=["b"], privileges=["c"]))

    def test_update_error(self):
        cred = DeveloperCredential(self.dummy_item)
        
        cred.session.post.return_value = MagicMock(
            json=lambda: {"error": "fail"},
            raise_for_status=lambda: None,
        )
        with self.assertRaises(Exception):
            cred.update(redirect_uris=["a"])

    def test_revoke(self):
        cred = DeveloperCredential(self.dummy_item)
        cred.session.post.return_value = MagicMock(
            json=lambda: {"success": True},
            raise_for_status=lambda: None,
        )
        self.assertTrue(cred.revoke(slot=1))

    def test_generate_token_calls_private(self):
        cred = DeveloperCredential(self.dummy_item)
        cred._generate_api_token = lambda slot, regen, exp: {"token": "abc"}
        self.assertEqual(cred.generate_token(slot=1), {"token": "abc"})
        cred._item = None
        with self.assertRaises(ValueError):
            cred.generate_token()

    def test_regenerate_token_calls_private(self):
        cred = DeveloperCredential(self.dummy_item)
        cred._generate_api_token = lambda slot, regen, exp: {"token": "abc"}
        self.assertEqual(cred.regenerate_token(slot=2), {"token": "abc"})
        cred._item = None
        with self.assertRaises(ValueError):
            cred.regenerate_token()

    def test_generate_api_token_errors(self):
        cred = DeveloperCredential(self.dummy_item)
        cred._gis.version = [2024, 1]
        with self.assertRaises(Exception):
            cred._generate_api_token()
        cred._gis.version = [2025, 1]
        cred._item.type = "NotApp"
        with self.assertRaises(ValueError):
            cred._generate_api_token()
        cred._item.type = "Application"
        cred._item.app_info = None
        with self.assertRaises(Exception):
            cred._generate_api_token()
        cred._item.app_info = {"client_id": "cid", "client_secret": "csecret"}
        with self.assertRaises(ValueError):
            cred._generate_api_token(slot=3)

class TestDeveloperCredentialManager(unittest.TestCase):
    def setUp(self):
        self.dummy_gis = DummyGIS()

    def test_init(self):
        mgr = DeveloperCredentialManager(self.dummy_gis)
        self.assertEqual(mgr._gis, self.dummy_gis)
        self.assertEqual(mgr.session, self.dummy_gis.session)

    def test_create(self):
        mgr = DeveloperCredentialManager(self.dummy_gis)
        import datetime
        expiration = datetime.datetime.now() + datetime.timedelta(days=1)
        cred = mgr.create(
            title="t",
            privileges=[TokenPrivilege.PORTAL_USER_CREATEGROUP, "portal:user:createItem"],
            referers=["http://a"],
            expiration=expiration,
            tags=["tag"],
            snippet="snip",
        )
        self.assertIsInstance(cred, DeveloperCredential)

    def test_create_expiration_error(self):
        mgr = DeveloperCredentialManager(self.dummy_gis)
        import datetime
        expiration = datetime.datetime.now() + datetime.timedelta(weeks=53)
        with self.assertRaises(ValueError):
            mgr.create(
                title="t",
                privileges=["portal:user:createItem"],
                referers=["http://a"],
                expiration=expiration,
            )

    def test_create_type_errors(self):
        mgr = DeveloperCredentialManager(self.dummy_gis)
        import datetime
        expiration = datetime.datetime.now() + datetime.timedelta(days=1)
        with self.assertRaises(ValueError):
            mgr.create(
                title="t",
                privileges=["portal:user:createItem"],
                referers="notalist",
                expiration=expiration,
            )
        with self.assertRaises(ValueError):
            mgr.create(
                title="t",
                privileges=["portal:user:createItem"],
                referers=["a"],
                redirect_uris="notalist",
                expiration=expiration,
            )
        with self.assertRaises(ValueError):
            mgr.create(
                title="t",
                privileges=[123],
                referers=["a"],
                expiration=expiration,
            )

    def test_get(self):
        mgr = DeveloperCredentialManager(self.dummy_gis)
        cred = mgr.get("abc123")
        self.assertIsInstance(cred, DeveloperCredential)

    def test_list(self):
        mgr = DeveloperCredentialManager(self.dummy_gis)
        creds = list(mgr.list())
        self.assertTrue(all(isinstance(c, DeveloperCredential) for c in creds))

if __name__ == "__main__":
    unittest.main()