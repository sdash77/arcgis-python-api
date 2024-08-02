import sys

#
#  Update the Path to set the test area
import logging
import uuid
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS, RoleManager, Role
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
class Test_CloneRoles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis_source = GIS(profile=profiles[0], set_active=False)
        rm: RoleManager = cls.gis_source.users.roles
        role1 = rm.create(
            name=f"role_{uuid.uuid4().hex[:5]}",
            description="description",
            privileges=[
                "portal:user:joinGroup",
                "portal:user:joinNonOrgGroup",
                "portal:user:viewOrgGroups",
            ],
        )
        cls.roles = [
            rm.create(
                name=f"role_{uuid.uuid4().hex[:5]}",
                description="description",
            ),
            role1,
        ]

    def test_role_clone_AGO_to_Ent(self):
        """AGO to Enterprise"""
        gis = GIS(profile=profiles[1])
        roles = gis.users.roles.clone(self.roles)
        assert len(roles) == len(self.roles)
        [g.result().delete() for g in roles]

    def test_role_clone_Ent_to_AGO(self):
        """Enterprise to AGO"""
        gis_source = GIS(profile=profiles[1], set_active=False)
        rm: RoleManager = gis_source.users.roles
        role1 = rm.create(
            name=f"role_{uuid.uuid4().hex[:5]}",
            description="description",
            privileges=[
                "portal:user:joinGroup",
                "portal:user:joinNonOrgGroup",
                "portal:user:viewOrgGroups",
            ],
        )
        roles = [
            rm.create(
                name=f"role_{uuid.uuid4().hex[:5]}",
                description="description",
            ),
            role1,
        ]
        self.roles.extend(roles)
        gis = GIS(profile=profiles[0])
        cloned_roles = gis.users.roles.clone(roles)
        assert len(cloned_roles) == len(roles)

        [g.result().delete() for g in cloned_roles]

    @classmethod
    def tearDownClass(cls):
        [g.delete() for g in cls.roles]


if __name__ == "__main__":
    unittest.main()
