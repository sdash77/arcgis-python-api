import uuid
import unittest
from utils.decorators import integration_test, profiles


@profiles.admin_agol
@integration_test
class TestLicenseProvisions(unittest.TestCase):
    def test_assign_provisions(self):
        """tests assign provision"""
        um = self.gis.users
        username = f"t3rdpart{uuid.uuid4().hex[:4]}"
        try:

            um.create(
                username=username,
                password="sup3r5ecr3t!",
                firstname="test",
                lastname="account",
                email="achapkowski@esri.com",
                role='org_user'
            )
            user = self.gis.users.get(username)
        except Exception as e:
            print(e)
            user = self.gis.users.get(username)

        lm = self.gis.admin.license
        for license in lm.all():
            if license.properties.listing.title == "TRIAL PAID \xa0LBU":

                license.assign(
                    username=user.username,
                    entitlements=["d01b2c63d1a14f63842c20076e3f2b66"],
                )
                assert license.all()

        assert user.delete()

    def test_revoke_provisions(self):
        """tests revoke provision"""
        gis = self.gis
        um = gis.users
        username = f"t3rdpart{uuid.uuid4().hex[:4]}"
        try:

            um.create(
                username=username,
                password="sup3r5ecr3t!",
                firstname="test",
                lastname="account",
                email="achapkowski@esri.com",
                role="viewer"
            )
            user = gis.users.get(username)
        except Exception as e:
            print(e)
            user = gis.users.get(username)

        lm = gis.admin.license
        for license in lm.all():
            if license.properties.listing.title == "TRIAL PAID \xa0LBU":

                license.assign(
                    username=user.username,
                    entitlements=["d01b2c63d1a14f63842c20076e3f2b66"],
                )
                assert license.all()
                for l in license.all():
                    entitlements = l["entitlements"]
                    license.revoke(username=user.username, entitlements=entitlements)
                assert len(license.all()) == 0

        assert user.delete()

    def test_lmgr_provisions(self):
        gis = self.gis
        lm = gis.admin.license
        user = gis.users.me
        p1 = lm.provisions(
            user=user,
            all_available=False,
            included_expired=True,
            return_client_ids=False,
        )
        p2 = lm.provisions(
            user=user,
            all_available=True,
            included_expired=True,
            return_client_ids=False,
        )
        p3 = lm.provisions(
            user=user,
            all_available=True,
            included_expired=True,
            return_client_ids=True,
        )
        p4 = lm.provisions(
            user=user,
            all_available=True,
            included_expired=False,
            return_client_ids=False,
        )


if __name__ == "__main__":
    unittest.main()
