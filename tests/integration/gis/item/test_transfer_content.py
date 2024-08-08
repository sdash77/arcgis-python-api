import sys
import logging
import unittest
import concurrent.futures
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS, UserManager, ContentManager, Item
from integration.config import QALAB_ROOT_PATH
from utils.decorators import integration_test

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ['your_online_admin_profile', 'your_enterprise_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class TestTransferContentAGOL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis: GIS = GIS(
            profile=profiles[0], verify_cert=False, proxy=PROXIES
        )
        um: UserManager = cls.gis.users
        import uuid

        username = f"RUser{uuid.uuid4().hex[:4]}"
        password = f"b!{uuid.uuid4().hex[:8]}A"
        cls.user = um.create(
            username=username,
            password=password,
            firstname="Danny",
            lastname="Human",
            email='testsadf@esri.com',
        )

        cls.fp = QALAB_ROOT_PATH + r"\transfer_content\transfer_content.csv"
        cls.item = cls.gis.content.add(
            item_properties={
                "type": "CSV",
                "title": "transfer_content_CSV",
            },
            data=cls.fp,
            owner=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        [i.delete() for i in cls.user.items()]
        cls.user.delete()

    def test_transfer_content_no_folder(self):
        """
        no folder + username as User
        """
        itemid = self.item.itemid
        r = self.user.transfer_content(
            self.gis.users.me, folder=self.user.username
        )
        assert isinstance(r, concurrent.futures.Future)
        assert r.result()
        item: Item = self.gis.content.get(itemid)
        item.reassign_to(self.user.username)

    def test_transfer_content_no_folder_test2(self):
        """
        no folder + username a string
        """
        itemid = self.item.itemid
        r = self.user.transfer_content(
            self.gis.users.me.username,
        )
        assert isinstance(r, concurrent.futures.Future)
        assert r.result()
        item: Item = self.gis.content.get(itemid)
        item.reassign_to(self.user.username)

    def test_transfer_content_folder(self):
        """
        folder + username as User
        """
        itemid = self.item.itemid
        r = self.user.transfer_content(
            self.gis.users.me, folder=self.user.username
        )
        assert isinstance(r, concurrent.futures.Future)
        assert r.result()
        item: Item = self.gis.content.get(itemid)
        item.reassign_to(self.user.username)


@unittest.skip("testing agol")
@integration_test
class TestTransferContentENT(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis: GIS = GIS(
            profile=profiles[1], verify_cert=False, proxy=PROXIES
        )
        um: UserManager = cls.gis.users
        import uuid

        username = f"RUser{uuid.uuid4().hex[:4]}"
        password = f"b!{uuid.uuid4().hex[:8]}A"
        cls.user = um.create(
            username=username,
            password=password,
            firstname="Danny",
            lastname="Human",
            email='testsadf@esri.com',
        )

        cls.fp = QALAB_ROOT_PATH + r"\transfer_content\transfer_content.csv"
        cls.item = cls.gis.content.add(
            item_properties={
                "type": "CSV",
                "title": "transfer_content_CSV",
            },
            data=cls.fp,
            owner=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        [i.delete() for i in cls.user.items()]
        cls.user.delete()

    def test_transfer_content_no_folder(self):
        """
        no folder + username as User
        """
        itemid = self.item.itemid
        r = self.user.transfer_content(
            self.gis.users.me, folder=self.user.username
        )
        assert isinstance(r, concurrent.futures.Future)
        assert r.result()
        item: Item = self.gis.content.get(itemid)
        item.reassign_to(self.user.username)

    def test_transfer_content_no_folder_test2(self):
        """
        no folder + username a string
        """
        itemid = self.item.itemid
        r = self.user.transfer_content(
            self.gis.users.me.username,
        )
        assert isinstance(r, concurrent.futures.Future)
        assert r.result()
        item: Item = self.gis.content.get(itemid)
        item.reassign_to(self.user.username)

    def test_transfer_content_folder(self):
        """
        folder + username as User
        """
        itemid = self.item.itemid
        r = self.user.transfer_content(
            self.gis.users.me, folder=self.user.username
        )
        assert isinstance(r, concurrent.futures.Future)
        assert r.result()
        item: Item = self.gis.content.get(itemid)
        item.reassign_to(self.user.username)


if __name__ == "__main__":
    unittest.main()
