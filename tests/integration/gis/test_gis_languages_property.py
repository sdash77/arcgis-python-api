import sys, uuid
import unittest
from arcgis.gis import GIS, UserManager, User
from utils.decorators import integration_test

profiles = [
    None,
    "your_online_admin_profile",
    "your_ent_admin_profile",
]
VERIFY_CERT = False
TRUST_ENV = True


@integration_test
class TestLanguagesRegionEndpoint(unittest.TestCase):
    def test_languages(self):
        """tests getting the languages registered with the enterprise"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=TRUST_ENV)
            assert gis.languages

    def test_regions(self):
        """tests getting the regions registered with the enterprise"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=TRUST_ENV)
            assert gis.regions

    def test_error_raised_culture(self):
        """ensures culture/language valueerror is working"""
        for profile in [p for p in profiles if p]:
            user = None
            try:
                gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=TRUST_ENV)
                um = gis.users
                isinstance(um, UserManager)
                user = um.create(
                    username=f"randouser{uuid.uuid4().hex[:3]}",
                    password=f"!1A{uuid.uuid4().hex[:5]}",
                    firstname="FirstName",
                    lastname="LastName",
                    email=f"{uuid.uuid4().hex[:5]}@esri.com",
                    description=None,
                    role=None,
                    provider="arcgis",
                    idp_username=None,
                    level=2,
                    thumbnail=None,
                    user_type=None,
                    credits=1,
                    groups=None,
                )
                with self.assertRaises(ValueError):
                    user.update(culture="NOT A CULTURE")
            except Exception as e:
                raise e
            finally:
                if user:
                    user.delete()

    def test_error_raised_region(self):
        """ensures region valueerror is working"""
        for profile in [p for p in profiles if p]:
            user = None
            try:
                gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=TRUST_ENV)
                um = gis.users
                isinstance(um, UserManager)
                user = um.create(
                    username=f"randouser{uuid.uuid4().hex[:3]}",
                    password=f"!1A{uuid.uuid4().hex[:5]}",
                    firstname="FirstName",
                    lastname="LastName",
                    email=f"{uuid.uuid4().hex[:5]}@esri.com",
                    description=None,
                    role=None,
                    provider="arcgis",
                    idp_username=None,
                    level=2,
                    thumbnail=None,
                    user_type=None,
                    credits=1,
                    groups=None,
                )
                with self.assertRaises(ValueError):
                    user.update(region="NOT A REGION")
            except Exception as e:
                raise e
            finally:
                if user:
                    user.delete()

    def test_update_with_region(self):
        """ensures region validates is working"""
        for profile in [p for p in profiles if p]:
            user = None
            try:
                gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=TRUST_ENV)
                um = gis.users
                isinstance(um, UserManager)
                user = um.create(
                    username=f"randouser{uuid.uuid4().hex[:3]}",
                    password=f"!1A{uuid.uuid4().hex[:5]}",
                    firstname="FirstName",
                    lastname="LastName",
                    email=f"{uuid.uuid4().hex[:5]}@esri.com",
                    description=None,
                    role=None,
                    provider="arcgis",
                    idp_username=None,
                    level=2,
                    thumbnail=None,
                    user_type=None,
                    credits=1,
                    groups=None,
                )
                region_selections = [g["region"] for g in gis.regions if g]
                rs = region_selections[0]
                if user.region == rs:
                    rs = region_selections[1]
                user.update(region=rs)
                assert user.region == rs
            except Exception as e:
                raise e
            finally:
                if user:
                    user.delete()

    def test_setting_culture_and_format(self):
        """The languages is used in the update operation of the user. We use the
        `GIS.lanaguages` to validate it."""
        for profile in [p for p in profiles if p]:
            user = None
            try:
                gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=TRUST_ENV)
                culture = [l["culture"] for l in gis.languages]
                um = gis.users
                isinstance(um, UserManager)
                user = um.create(
                    username=f"randouser{uuid.uuid4().hex[:3]}",
                    password=f"!1A{uuid.uuid4().hex[:5]}",
                    firstname="FirstName",
                    lastname="LastName",
                    email=f"{uuid.uuid4().hex[:5]}@esri.com",
                    description=None,
                    role=None,
                    provider="arcgis",
                    idp_username=None,
                    level=2,
                    thumbnail=None,
                    user_type=None,
                    credits=1,
                    groups=None,
                )
                new_culture = culture[0]
                if user.culture == new_culture:
                    new_culture = culture[1]
                assert new_culture != user.culture
                user.update(culture=new_culture)
                assert user.culture == new_culture
            except Exception as e:
                raise e
            finally:
                if user:
                    user.delete()


if __name__ == "__main__":
    unittest.main()
