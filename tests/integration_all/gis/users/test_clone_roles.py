import uuid
import unittest
from arcgis.gis import RoleManager
from utils.decorators import integration_test, from_to_profiles
from utils._logging import enable_verbose_logging


enable_verbose_logging()


@from_to_profiles.all_except_k8s
@integration_test
class TestCloneRoles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rm: RoleManager = cls.from_gis.users.roles
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

    def test_role_clone(self):
        """tests roles clone workflows"""
        roles = self.to_gis.users.roles.clone(self.roles)
        assert len(roles) == len(self.roles)
        [g.result().delete() for g in roles]


if __name__ == "__main__":
    unittest.main()
