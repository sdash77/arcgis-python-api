import unittest
from utils._logging import enable_verbose_logging
from utils.decorators import integration_test, profiles

enable_verbose_logging()


@unittest.skip("Manual test, comment this decorator to run")
@profiles.admin_enterprise
@integration_test
class TestMode(unittest.TestCase):
    def test_set_readonly(self):
        """tests setting the portal to read only mode"""
        assert self.gis
        assert self.gis.users.me
        self.gis.admin.mode = {'read_only': True}
        assert self.gis.admin.mode
        assert self.gis.admin.mode.get('isReadOnly') is True, "Expected read only mode to be True"

        self.gis.admin.mode = None
        assert self.gis.admin.mode.get('isReadOnly') is False, "Expected read only mode to be False"


if __name__ == "__main__":
    unittest.main()
