import sys, os, uuid
import unittest, logging
from utils.decorators import profiles, integration_test
from utils._logging import enable_verbose_logging

from arcgis.gis import GIS, Item, Group

try:

    from integration.config import QALAB_ROOT_PATH
except:
    from .integration.config import QALAB_ROOT_PATH

enable_verbose_logging()
_log = logging.getLogger()

_TEST_DATASET = (
    rf"{QALAB_ROOT_PATH}\group_manager_data\migration_dataset.zip"
)


@profiles.enterprise
@integration_test
class TestGroupMigrationByName(unittest.TestCase):
    def test_export_name(self):
        from arcgis.gis import GIS

        gis: GIS = self.gis
        source_data_name: str = f"Parkinglots{uuid.uuid4().hex[:4]}"
        group_name: str = f"Migration{uuid.uuid4().hex[:4]}"
        epk_file_name: str = f"mysuperfunfile{uuid.uuid4().hex[:2]}"
        if gis.version >= [2024, 1] and os.path.isfile(_TEST_DATASET):
            for i in gis.content.search(source_data_name):
                assert i.delete()
            pitem: Item = gis.content.add(
                {
                    "title": source_data_name,
                    "tags": ["a", "b", "c"],
                    'type': "Shapefile",
                },
                data=_TEST_DATASET,
            )
            published_item: Item = pitem.publish()
            for grp in gis.groups.search(group_name):
                assert grp.delete()
            new_group: Group = gis.groups.create(
                title=group_name, tags="a,b,c"
            )

            pitem.sharing.groups.add(new_group)

            published_item.sharing.groups.add(new_group)

            epk_file: Item = new_group.migration.create(
                [pitem], epk_file_name, future=False
            )  #  returns an Item
            assert epk_file.name == f"{epk_file_name}.epk"
            assert epk_file.delete()
            assert new_group.delete()
            assert published_item.delete()
            assert pitem.delete()
        else:
            self.skipTest(
                "The enterprise does not support the output name, skipping test."
            )


if __name__ == "__main__":
    unittest.main()
