import sys
import unittest
from arcgis.gis import GIS
from utils.decorators import integration_test


@integration_test
class TestMarketPlaceManager(unittest.TestCase):
    """Tests the <username>/report API"""

    def test_get_listings(self):
        gis = GIS(profile="your_ent_admin_profile", verify_cert=False, trust_env=True)
        cnt = gis.content
        mrkt = cnt.marketplace
        listings = mrkt.listings(query="*", my_listings=True)
        assert listings
        assert len(listings["listings"]) > 0

        listing = mrkt.listing(itemid=listings["listings"][0]["itemId"])
        assert listing
        assert listing["itemId"] == listings["listings"][0]["itemId"]

    def test_get_purchases(self):
        gis = GIS(profile="your_ent_admin_profile", verify_cert=False, trust_env=True)
        cnt = gis.content
        mrkt = cnt.marketplace
        purchases = mrkt.purchases()
        assert purchases
        assert isinstance(purchases["purchases"], list)
        assert isinstance(purchases["trials"], list)
        assert isinstance(purchases["interests"], list)

    def test_get_customer_list(self):
        gis = GIS(profile="your_ent_admin_profile", verify_cert=False, trust_env=True)
        cnt = gis.content
        mrkt = cnt.marketplace
        listings = mrkt.listings(query="*", my_listings=True)

        customer_list = mrkt.customer_list(itemid=listings["listings"][0]["itemId"])
        assert customer_list
        assert isinstance(customer_list["purchases"], list)
        assert isinstance(customer_list["trials"], list)
        assert isinstance(customer_list["interests"], list)

    def test_user_entitlements(self):
        gis = GIS(profile="your_ent_admin_profile", verify_cert=False, trust_env=True)
        cnt = gis.content
        mrkt = cnt.marketplace
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
