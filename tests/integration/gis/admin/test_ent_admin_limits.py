import unittest
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging

enable_verbose_logging()


@profiles.admin_enterprise
@integration_test
class TestEnterpriseLimits(unittest.TestCase):
    def test_get_limits(self):
        system = self.gis.admin.system
        assert system.limits

    def test_set_limits(self):
        result = self.gis.admin.system.set_limits(
            properties=[{'limitName': 'TaskRunHistoryCount', 'numLimit': 50}]
        )
        assert result


if __name__ == "__main__":
    unittest.main()
