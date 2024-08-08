import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
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


profiles = ['your_online_admin_profile', 'your_ent_admin_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class Test_CanReassignItems(unittest.TestCase):
    def test_can_reassign_single_user(self):
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            users = [
                user
                for user in gis.users.search("*")
                if user.disabled == False and user.username != gis.users.me.username
            ]
            if len(users) >= 2:
                user1 = users[0]
                user2 = users[1]
                items = user1.items()
                try:
                    result = gis.content.can_reassign(items, gis.users.me)
                    assert isinstance(result, list)
                except Exception as e:
                    print(e)

    def test_can_reassign_items_multiple_users(self):
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            users = [
                user
                for user in gis.users.search("*")
                if user.disabled == False and user.username != gis.users.me.username
            ]
            if len(users) >= 2:
                user1 = users[0]
                user2 = users[1]
                items = gis.users.me.items()
                try:
                    result = gis.content.can_reassign(items, gis.users.me)
                    assert isinstance(result, list)
                except Exception as e:
                    print(profile)
                    print(user1, gis.users.me)
                    print(e)


if __name__ == "__main__":
    unittest.main()
