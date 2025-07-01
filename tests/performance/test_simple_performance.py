import unittest
import functools
import time

from arcgis.features import FeatureLayer
from arcgis.gis import GIS


def timer(func):
    """Decorator: Print the runtime of the decorated function

    Args:
      func (function): The function to profile

    Returns:
      The function wrapper: The runtime of the function in seconds
    """

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        """

        Args:
          *args:
          **kwargs:

        Returns:

        """
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f"Finished running {func.__name__!r} in {run_time:.4f} seconds.")
        return run_time

    return wrapper_timer


class TestSimplePerformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(
            "https://dev0016752.esri.com/portal", "admin", "esri.agp", verify_cert=False
        )
        cls.layer_url = (
            "https://dev0016752.esri.com/server/rest/services/HCADFull/FeatureServer/15"
        )

    def test_construct_gis(self):
        url = "https://dev0016752.esri.com/portal"
        username = "admin"
        password = "esri.agp"

        @timer
        def construct_gis():
            return GIS(url, username, password, verify_cert=False)

        val = construct_gis()
        assert val < 2, f"Query 1,000 feature took too long: {val}"

    def test_query_feature_layer_100_features(self):
        fl = FeatureLayer(self.layer_url)

        @timer
        def query_feature_layer_100_features():
            return fl.query(where="objectid < 100")

        val = query_feature_layer_100_features()
        assert val < 1, f"Query 1,000 feature took too long: {val}"

    def test_query_feature_layer_1000_features(self):
        fl = FeatureLayer(self.layer_url)

        @timer
        def query_feature_layer_1000_features():
            return fl.query(where="objectid < 1000")

        val = query_feature_layer_1000_features()
        assert val < 1, f"Query 1,000 feature took too long: {val}"

    def test_query_feature_layer_10000_features(self):
        fl = FeatureLayer(self.layer_url)

        @timer
        def query_feature_layer_10000_features():
            return fl.query(where="objectid < 10000")

        val = query_feature_layer_10000_features()
        assert val < 9, f"Query 10,000 feature took too long: {val}"

    def test_create_single_folder(self):
        uid = int(time.time())
        folder_name = f"performance_test_{uid}"

        @timer
        def create_single_folder():
            try:
                return self.gis.content.folders.create(folder_name)
            except Exception as ex:
                print(ex)

        val = create_single_folder()

        created_folder = self.gis.content.folders.get(folder_name)
        if created_folder:
            created_folder.delete(folder_name)

        assert val < 1, f"Create new folder took too long: {val}"

    @unittest.skip("Skip until `user_defaults` param is ready")
    def test_create_user(self):
        # Create user data
        uid = int(time.time())
        user_name = f"performance_user_{uid}"
        user_password = "IL0veMyGI$_4Ever"
        last_name = "dino"
        role_list = ["org_publisher"]
        email = "a@b.com"

        @timer
        def create_user():
            return self.gis.users.create(
                user_name,
                user_password,
                user_name,
                last_name,
                email,
                role=role_list[0],
                use_defaults=True,
            )

        val = create_user()
        new_user = self.gis.users.get(user_name)
        self.gis.users.delete_users([new_user])
        self.assertTrue(val < 1, f"Create new folder took too long: {val}")
