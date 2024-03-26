import unittest, re, os
from arcgis.gis import GIS
from arcgis.gis.clone import (
    BaseCloneTextItemDefinition,
    register,
    unregister,
    clone_registry,
)
from arcgis.gis import Item
from arcgis._impl.common._clone import (
    _TextItemDefinition,
    _NotebookDefinition,
    _search_org_for_existing_item,
    _share_item_with_groups,
    _get_org_url,
    _ItemCreateException,
)
from utils.decorators import integration_test


class ClassCustomItemDef(BaseCloneTextItemDefinition):
    def __init__(
        self,
        target,
        clone_mapping,
        info,
        source_url,
        data=None,
        sharing=None,
        thumbnail=None,
        portal_item=None,
        folder=None,
        item_extent=None,
        search_existing=True,
        owner=None,
        **kwargs,
    ):
        super().__init__(
            target,
            clone_mapping,
            info,
            data,
            sharing,
            thumbnail,
            portal_item,
            folder,
            item_extent,
            search_existing,
            owner,
            preserve_item_id=kwargs.get("preserve_item_id", False),
        )
        self._preserve_item_id = kwargs.pop("preserve_item_id", False)
        self._source_url = source_url

    def clone(self):
        """Clone the python notebook in the target organization."""
        try:
            new_item = None
            original_item = self.info
            if self._search_existing:
                new_item = _search_org_for_existing_item(self.target, self.portal_item)
            if not new_item:

                # Get the item properties from the original item to be applied when the new item is created
                item_properties = self._get_item_properties(self.item_extent)

                # Add the new item
                new_item = self._add_new_item(item_properties)

                # Find and replace all item and group id references
                notebook = self.data
                notebook_json = ""

                with open(notebook, "r", encoding="utf8") as file:
                    notebook_json = file.read()

                for key, value in self._clone_mapping["Item IDs"].items():
                    notebook_json = re.sub(key, value, notebook_json, 0, re.IGNORECASE)
                for key, value in self._clone_mapping["Group IDs"].items():
                    notebook_json = re.sub(key, value, notebook_json, 0, re.IGNORECASE)
                notebook_json = re.sub(
                    self._source_url,
                    _get_org_url(self.target),
                    notebook_json,
                    0,
                    re.IGNORECASE,
                )

                new_notebook = os.path.join(
                    os.path.dirname(notebook), "{0}.ipynb".format(new_item.id)
                )
                with open(new_notebook, "w", encoding="utf8") as file:
                    file.write(notebook_json)

                # Update python notebook
                new_item.update(data=new_notebook)

            _share_item_with_groups(
                new_item, self.sharing, self._clone_mapping["Group IDs"]
            )
            self.resolved = True
            self._clone_mapping["Item IDs"][original_item["id"]] = new_item["id"]
            return new_item

        except Exception as ex:
            raise _ItemCreateException(
                "Failed to create {0} {1}: {2}".format(
                    original_item["type"], original_item["title"], str(ex)
                ),
                new_item,
            )


@unittest.skip("I work")
@integration_test
class TestCloningExtension(unittest.TestCase):
    def test_registry_checker(self):
        """asserts the get of the registry for cloning"""
        registry = clone_registry()
        assert isinstance(registry, dict)

    def test_register(self):
        """checks the registration logic"""
        assert register("Notebook", ClassCustomItemDef)
        registry = clone_registry()
        assert "Notebook" in registry

        class A:
            pass

        assert register("FAKE", A) == False

    def test_unregister(self):
        """checks the unregistration logic"""
        assert register("Notebook", ClassCustomItemDef)
        registry = clone_registry()
        assert "Notebook" in registry
        assert unregister("Notebook")
        registry = clone_registry()
        assert len(clone_registry()) == 0
        assert unregister("Notebook") == False


@integration_test
class TestCustomCloning(unittest.TestCase):
    def setUp(self):
        self._source = GIS(
            profile="your_online_admin_profile", verify_cert=False, trust_env=True
        )
        self._target = GIS(
            profile="your_ent_admin_profile", verify_cert=False, trust_env=True
        )

    def test_custom_cloning(self):
        """tests using a"""
        items = self._source.content.get("d97fb09b1ca140b88e43cfa4ee711346")
        assert register("Notebook", ClassCustomItemDef)
        results = self._target.content.clone_items([items])
        assert all([result.delete() for result in results])


if __name__ == "__main__":
    unittest.main()
