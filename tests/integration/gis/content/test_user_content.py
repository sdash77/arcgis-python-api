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
        if len(users) > 0:
            user: User = users[-1]
            folders = list(user.folders)
            if len(folders) > 0:
                folder= folders[0]
                assert folder
                assert isinstance(list(user.items(folder, 1)), list)
    

if __name__ == "__main__":
    unittest.main()