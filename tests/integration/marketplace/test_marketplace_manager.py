import sys

sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")
import unittest
from arcgis.gis import GIS


class TestMarketPlaceManager(unittest.TestCase):
    """Tests the <username>/report API"""

    def test_get_listings(self):
        gis = GIS(profile="your_enterprise_profile", verify_cert=False, trust_env=True)
        cnt = gis.content
        mrkt = cnt.marketplace_manager
        listings = mrkt.listings(query="*", my_listings=True)
        assert listings
        assert len(listings["listings"]) > 0

        listing = mrkt.listing(itemid=listings["listings"][0]["itemId"])
        assert listing
        assert listing["itemId"] == listings["listings"][0]["itemId"]

    def test_get_purchases(self):
        gis = GIS(profile="your_enterprise_profile", verify_cert=False, trust_env=True)
        cnt = gis.content
        mrkt = cnt.marketplace_manager
        purchases = mrkt.purchases()
        assert purchases
        assert purchases["purchases"]
        assert purchases["trials"]
        assert purchases["interests"]

    def test_get_customer_list(self):
        gis = GIS(profile="your_enterprise_profile", verify_cert=False, trust_env=True)
        cnt = gis.content
        mrkt = cnt.marketplace_manager
        listings = mrkt.listings(query="*", my_listings=True)

        customer_list = mrkt.customer_list(itemid=listings["listings"][0]["itemId"])
        assert customer_list
        assert customer_list["purchases"]
        assert customer_list["trials"]
        assert customer_list["interests"]

    def test_user_entitlements(self):
        gis = GIS(profile="your_enterprise_profile", verify_cert=False, trust_env=True)
        cnt = gis.content
        mrkt = cnt.marketplace_manager
        listings = mrkt.listings(query="*", my_listings=True)
        listing = listings["listings"][2]

        user_entitlements = mrkt.user_entitlements(itemid=listing["itemId"])
        assert user_entitlements

        user_entitlement = mrkt.user_entitlement(
            itemid=listing["itemId"], username=gis.users.me.username
        )
        assert user_entitlement


if __name__ == "__main__":
    unittest.main()
