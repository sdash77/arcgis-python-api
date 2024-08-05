import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from arcgis.gis.admin._security import PasswordPolicy
from utils.decorators import integration_test

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ['your_online_admin_profile', 'your_ent_admin_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class TestPasswordPolicyAGOL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(profile=profiles[0], verify_cert=False, proxy=PROXIES)
        cls.pp: PasswordPolicy = cls.gis.admin.password_policy

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


@integration_test
class TestPasswordPolicyENT(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(profile=profiles[1], verify_cert=False, proxy=PROXIES)
        cls.pp: PasswordPolicy = cls.gis.admin.password_policy

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
