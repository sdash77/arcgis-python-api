import unittest
import json
from utils.decorators import integration_test, profiles

@profiles.admin_enterprise_and_agol
@integration_test
class TestUserResourceManagerIntegration(unittest.TestCase):

    def test_user_resources_property(self):
        resources = self.gis.users.me.resources
        self.assertIsNotNone(resources)
        self.assertEqual(resources._user.username, self.gis.users.me.username)

    def test_user_resources_add_and_list_and_remove(self):
        resources = self.gis.users.me.resources
        # Add a small text resource
        test_file_name = "test_resource.txt"
        test_text = {"file": "integration test resource content"}
        add_result = resources.add(file_name=test_file_name, text=json.dumps(test_text))
        self.assertTrue(add_result.get("success"))
        # List resources and check our file is present
        resource_list = list(resources.list())
        self.assertTrue(any(r["key"] == test_file_name for r in resource_list))
        
        # Get the resource and check its content
        resource = resources.get(test_file_name)
        self.assertIsNotNone(resource)
        self.assertEqual(resource, test_text)
        resources.remove(test_file_name)


if __name__ == "__main__":
    unittest.main()
