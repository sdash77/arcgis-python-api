import unittest
from utils.decorators import profiles, integration_test
from utils._logging import enable_verbose_logging

from arcgis.gis import GIS, User, UserManager

enable_verbose_logging()


@profiles.admin_enterprise_and_agol
@integration_test
class TestFeature(unittest.TestCase):
    def test_user_groups_over_20(self):
        """tests large batch of users"""
        gis: GIS = self.gis
        um: UserManager = gis.users
        users = um.advanced_search(
            query=f"orgid:{gis.properties.id}", max_users=50
        )['results']
        res = um.user_groups(users=users)
        assert isinstance(res, list)

    def test_user_groups_under_20(self):
        """tests a single user"""
        gis: GIS = self.gis
        um: UserManager = gis.users
        me: User = gis.users.me
        users = [me]
        res = um.user_groups(users=users)
        assert isinstance(res, list)


if __name__ == "__main__":
    unittest.main()
