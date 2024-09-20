# -------------------------------------------------------------------------------
# Name:        UserManager class tests
# Purpose:     Sanity tests for ArcGIS Python API
# -------------------------------------------------------------------------------
import unittest
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_precondition_checks import PortalUtils
from integration.dino_utils.dino_configs import DinoConfigs
from integration.config import QALAB_ROOT_PATH
from configparser import ConfigParser
import datetime
import os
from utils.decorators import integration_test

# region PreCondition check
test_skip = False
class_skip = False
module_skip = False

r1 = PreconditionChecks.check_API_import()
r2 = PreconditionChecks.check_Python_version()

if r1 & r2:
    print("## Precondition checks passed ##")
    module_skip = False
else:
    module_skip = True
    print("Pre condition checks failed. Quitting tests")
    raise (exit())

# Import the module after Precondition checks pass
try:
    import arcgis
    from arcgis.gis import GIS
except ImportError:
    print("API import error. Quitting test")
    raise (exit())
# endregion PreCondition Check

# TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in GIS module")
def setUpModule():
    """
    Set up code for full arcgis.gis module GIS class tests
    :return:
    """
    # Get environment status
    print("ArcPy on system: ", PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())


@integration_test
class Test_UserManager_portal_builtin(unittest.TestCase):
    """
    Test to check if a UserManager object works with builtin portal
    """

    @classmethod
    def setUpClass(cls):
        """
        Check if portal builtin can be reached
        Get class test asset location
        :return:
        """

        # region Read config data
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, "UTF-8")

        cls.portal_url = _conf_reader["teamportal"]["url"]
        cls.portal_username = _conf_reader["teamportal"]["admin_user"]
        cls.portal_password = _conf_reader["teamportal"]["admin_password"]

        _conf_reader2 = ConfigParser()
        _conf_reader2.read(DinoConfigs.root_init_file, "UTF-8")

        cls.qalab_base_path = QALAB_ROOT_PATH
        cls.qalab_cls_path = (
            cls.qalab_base_path + _conf_reader2["test_data"]["qalab_UserManager_cls"]
        )
        # endregion

        # region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(
            cls.portal_url, cls.portal_username, cls.portal_password, verify_cert=False
        )
        if cls.gis is None:
            cls.class_skip = True

        print("Portal version: " + PortalUtils.report_portal_version(cls.gis))
        print("==================================================================")
        print("Beginning tests in Test_UserManager_portal_builtin class")
        # endregion

    def setUp(self):
        test_skip = False  # reset the skip flag
        print("Test: " + self._testMethodName)
        self.namePrefix = "dino_UserManager_"

        t = datetime.datetime.now()
        self.time_stamp = str.format(
            "Time stamp: {0}_{1}_{2}_{3}_{4}_{5}",
            str(t.year),
            str(t.month),
            str(t.day),
            str(t.hour),
            str(t.minute),
            str(t.second),
        )
        print("Time stamp: " + self.time_stamp)

    def test_createUser_has_thumbnail(self):
        """
        Test to check if a new user has a thumbnail object
        :return:
        """
        thumbnail_path = os.path.join(self.qalab_cls_path, "Basemaps.png")
        try:
            # Create user data
            user_name = "user3x"
            user_password = "IL0veMyGI$_4Ever"
            last_name = "dino"
            role_list = ["org_publisher"]
            thumbnail = thumbnail_path
            email = "amani@esri.com"

            # Check if user is present, else create

            return_value = True

            try:
                print("Creating user: " + user_name, end=" ")
                user_obj_list = self.gis.users.get(user_name)
                if user_obj_list is None:
                    created_user = self.gis.users.create(
                        user_name,
                        user_password,
                        user_name,
                        last_name,
                        email,
                        thumbnail=thumbnail,
                        role=role_list[0],
                    )
                    if created_user is not None:
                        print("Created new user: " + user_name)
                        print(
                            "Checking if thumbnail object is present for user "
                            + user_name
                        )
                        thumbnail_obj = created_user.get_thumbnail()

                        if thumbnail_obj is not None:
                            print(
                                "Thumbnail object was found for new user: " + user_name
                            )

                    else:
                        print("Error: cannot create new user: " + user_name)
                else:
                    print(user_name + " already exists in this portal")
            except Exception as ex:
                print("Error running create_sample_user: " + ex.__str__())
                return_value = False

            self.assertTrue(return_value, "New User could not be created")
            self.assertIsNotNone(created_user, "New User could not be created")
            self.assertIsInstance(
                created_user,
                arcgis.gis.User,
                "gis.users.create() does not return a User object",
            )
            self.assertIsNotNone(
                thumbnail_obj, "Thumbnail object was not found for the new user"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def tearDown(self):
        print("------------------------------------------------------------------\n")

        if self._testMethodName == "test_createUser_has_thumbnail":

            user_name = "user3x"

            try:

                print("Deleting user: " + user_name, end=" ")
                user_obj_list = self.gis.users.get(user_name)
                if user_obj_list is not None:
                    deleted_user = user_obj_list.delete()
                    if deleted_user:
                        print("Deleted user: " + user_name)
                    else:
                        print("Error: cannot delete user: " + user_name)
                else:
                    print(user_name + " was not found in this portal")

                self.assertTrue(deleted_user, "User could not be deleted")

            except AssertionError as assertErrorException:
                test_skip = True
                raise assertErrorException

            except unittest.SkipTest as skipException:
                raise skipException

            except Exception as testException:
                self.fail("Error during test: " + testException.__str__())

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")


# TestModule
def tearDownModule():
    print("**End User Manager Tests**")


if __name__ == "__main__":
    unittest.main()
