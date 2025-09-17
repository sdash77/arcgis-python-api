import unittest
from utils.decorators import integration_test, profiles


@profiles.admin_enterprise
@integration_test
class TestMarketPlaceManager(unittest.TestCase):
    """Tests the MarketPlace APIs"""

    def test_get_listings(self):
        mrkt = self.gis.content.marketplace
        listings = mrkt.listings(query="*", my_listings=True)
        assert listings
        assert len(listings["listings"]) > 0

        listing = mrkt.listing(itemid=listings["listings"][0]["itemId"])
        assert listing
        assert listing["itemId"] == listings["listings"][0]["itemId"]

    def test_get_purchases(self):
        mrkt = self.gis.content.marketplace
        purchases = mrkt.purchases()
        assert purchases
        assert isinstance(purchases["purchases"], list)
        assert isinstance(purchases["trials"], list)
        assert isinstance(purchases["interests"], list)

    def test_get_customer_list(self):
        mrkt = self.gis.content.marketplace
        listings = mrkt.listings(query="*", my_listings=True)

        customer_list = mrkt.customer_list(itemid=listings["listings"][0]["itemId"])
        assert customer_list
        assert isinstance(customer_list["purchases"], list)
        assert isinstance(customer_list["trials"], list)
        assert isinstance(customer_list["interests"], list)

    def test_user_entitlements(self):
        mrkt = self.gis.content.marketplace
        listings = mrkt.listings(query="*", my_listings=True)
        listing = listings["listings"][2]

        user_entitlements = mrkt.user_entitlements(itemid=listing["itemId"])
        assert user_entitlements

        user_entitlement = mrkt.user_entitlement(
            itemid=listing["itemId"], username=self.gis.users.me.username
        )
        assert user_entitlement


if __name__ == "__main__":
    unittest.main()
