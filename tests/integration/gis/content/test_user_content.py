#######################################################################
import unittest
from utils.decorators import profiles, integration_test
from utils._logging import enable_verbose_logging
from arcgis.gis import User, GIS, Item
enable_verbose_logging()


@profiles.enterprise_and_agol
@integration_test
class TestUserContentMethods(unittest.TestCase):
    def test_item_folders(self):
        gis: GIS = self.gis
        users: list[User] = [user for user in gis.users.search("*") \
                             if user.role == 'org_admin']
        if len(users) == 0:
            self.skipTest("No valid users, skipping")
        
        user: User = users[-1]
        folder = next(user.folders)
        assert folder
        assert isinstance(list(user.items(folder, 1)), list)
    

if __name__ == "__main__":
    unittest.main()