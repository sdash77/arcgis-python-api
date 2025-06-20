import unittest
from arcgis.gis import GIS
from arcgis.gis.admin._security import PasswordPolicy
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging

enable_verbose_logging()


@profiles.admin_enterprise_and_agol
@integration_test
class TestPasswordPolicy(unittest.TestCase):
    def setUp(self):
        self.pp: PasswordPolicy = self.gis.admin.password_policy

    def test_password_policy_get(self):
        pp: PasswordPolicy = self.pp
        assert pp.properties
        assert pp.policy

    def test_password_policy_set(self):
        pp: PasswordPolicy = self.pp
        oldpolicy = dict(pp.policy)
        newpolicy = {
            "minLength": 9,
            "minLetter": 1,
            "minDigit": 1,
            "minOther": None,
        }
        pp.policy = newpolicy
        assert pp.policy
        pp.policy = oldpolicy

    def test_lockout_policy_get_set(self):
        pp: PasswordPolicy = self.pp
        assert pp.properties
        assert pp.lockout_policy
        default = {'maxInvalidAttempt': 5, 'lockoutPeriodInSeconds': 900}
        newpolicy = {'maxInvalidAttempt': 4, 'lockoutPeriodInSeconds': 1000}
        pp.lockout_policy = newpolicy
        assert pp.lockout_policy['maxInvalidAttempt'] == 4
        pp.lockout_policy = default


if __name__ == "__main__":
    unittest.main()
