import json
import uuid
import unittest
import arcgis
from arcgis.gis import ItemProperties
from arcgis.gis._impl._datastores import PortalDataStore
from arcgis.gis._impl._jb import StatusJob
from utils.decorators import integration_test, profiles


@integration_test
@profiles.admin_enterprise
class TestPortalDataStore(unittest.TestCase):
    """
    Tests the 10.7/10.7.1/10.8.1 functionality for Portal Datastores

    These tests focus primarily on scene package layers and bulk publishing of layers
    """

    def setUp(self):
        """set up datastore for each test"""
        server_list = self.gis.admin.federation.servers
        server = [server for server in server_list["servers"] if server["serverRole"] == "HOSTING_SERVER"][0]
        self.server_id = server["id"]
        h = uuid.uuid4().hex[:5]
        info = {
            "info": {
                "isManaged": False,
                "dataStoreConnectionType": "replicated",
                "path": "/mnt/testDatastore",
            },
            "type": "folder",
            "path": "/fileShares/ajc_folder_test",
            "clientPath": "/mnt/testDatastore",
        }
        txt = json.dumps(info)

        folder = self.gis.content.folders._get_or_create("integration_testing")
        self.item = folder.add(
            item_properties=ItemProperties(
                title=f"datastore_{h}",
                item_type="Data Store",
                tags=["erase me", "integration testing"],
            ),
            text=txt,
        ).result()

    def tearDown(self):
        """remove datastore after test"""
        self.gis.datastore.unregister(item=self.item, server_id=self.server_id)
        self.item.delete()

    def test_validate(self):
        """tests the validate operation on portal"""
        assert self.gis.datastore.register(item=self.item, server_id=self.server_id)
        assert self.gis.datastore.servers(item=self.item.itemid)
        ds_item_id = self.item.itemid
        server_id = self.server_id
        assert self.gis.datastore.validate(server_id=server_id, item=ds_item_id)
        ds_item = self.gis.content.get(ds_item_id)
        assert self.gis.datastore.validate(server_id=server_id, item=ds_item)

    def test_servers(self):
        """tests the server method"""
        assert self.gis.datastore.register(item=self.item, server_id=self.server_id)
        assert self.gis.datastore.servers(item=self.item.itemid)
        assert isinstance(self.gis.datastore.servers(item=self.item.itemid), list)
        assert self.gis.datastore.servers(item=self.item.itemid)[0]["serverRole"] == "HOSTING_SERVER"

    def test_layers(self):
        """tests that layers for the datastore are returned as a list"""
        assert self.gis.datastore.register(item=self.item, server_id=self.server_id)
        layers = self.gis.datastore.layers(item=self.item)
        assert isinstance(layers, list)

    def test_datastore_root(self):
        """tests the datastore root properties"""
        assert isinstance(self.gis.datastore, PortalDataStore)
        assert self.gis.datastore.properties
        assert self.gis.datastore._all_datasets  # not used publicly

    def test_register_unregister_operations(self):
        """tests the unregister/register operation"""
        assert self.gis.datastore.register(item=self.item, server_id=self.server_id)
        assert self.gis.datastore.unregister(item=self.item, server_id=self.server_id)

    @unittest.skip("need stable egdb")
    # TODO: mount egdb in portal
    def test_publish_delete_layers(self):
        """tests the publish/delete all layers operations"""
        network_path = (
            r"\\datalibrary\data\Europe\Austria\Salzburg"
        )
        h = uuid.uuid4().hex[:5]
        info = {
            "info": {
                "isManaged": False,
                "dataStoreConnectionType": "replicated",
                "path": network_path,
            },
            "type": "folder",
            "path": f"/fileShares/ajc_folder_{h}",
            "clientPath": network_path,
        }
        txt = json.dumps(info)

        folder = self.gis.content.folder._get_or_create("integration_testing")
        item = folder.add(
            item_properties=ItemProperties(
                title=f"datastore_{h}",
                item_type="Data Store",
                tags=["erase me", "integration testing"],
            ),
            text=txt,
        ).result()

        try:
            cfg = json.loads(
                """{"serviceName":"%s","type":"MapServer","capabilities":"Map","extensions":[{"typeName":"FeatureServer","capabilities":"Query","enabled":"true","properties":{"maxRecordCount":"3500"}}]}"""
                % uuid.uuid4().hex[:5]
            )
            assert self.gis.datastore.register(item=item, server_id=self.server_id)
            g = self.gis.datastore.publish_layers(
                item=item, srv_config=cfg, server_id=self.server_id
            )
            r = self.gis.datastore.delete_layers(item=item)
        except Exception as e:
            print(e)
            raise e
        finally:
            self.gis.datastore.unregister(item=item, server_id=self.server_id)
            item.delete()

    @unittest.skip("scene layer json file not ready yet in portal")
    # TODO: mount scene layer json file in portal
    def test_publish(self):
        """
        Tests the publishing of a single layer on Portal.
        """
        try:
            h = uuid.uuid4().hex[:5]
            # register data store
            self.gis.datastore.register(self.item, self.server_id)

            # query datastore for list of datasets
            datastore_id = self.item.get_data()["id"]
            datasets = self.gis.datastore.describe(
                self.item, server_id=self.server_id, path="/", store_type="datastore"
            ).result()

            if not "result" in datasets:
                datasets = self.gis.datastore.describe(
                    self.item, server_id=self.server_id, path="/", store_type="datastore"
                ).result()
            dataset_path = datasets["result"]["path"]

            # publish the scene layer
            service_config = {
                "type": "SceneServer",
                "serviceName": f"SanFran{h}",
                "properties": {
                    "pathInCachedStore": dataset_path,
                    "cacheStoreId": datastore_id,
                },
            }

            sl_item = self.gis.datastore.publish(
                config=service_config,
                server_id=self.server_id,
                folder=None,
                description="test",
                tags=["test"],
            )
            assert isinstance(sl_item.result(), list)
            assert all([isinstance(i, arcgis.gis.Item) for i in sl_item.result()])
            [i.delete() for i in sl_item.result()]
        except Exception as e:
            print(e)
            raise e

    def test_describe(self):
        """
        tests the describe asynchronous method
        """
        try:
            assert self.gis.datastore.register(item=self.item, server_id=self.server_id)
            j = self.gis.datastore.describe(
                self.item, server_id=self.server_id, path="/", store_type="datastore"
            )
            assert j
            assert isinstance(j, StatusJob)
            assert j.result()
        except Exception as e:
            print(e)
            raise e


if __name__ == "__main__":
    unittest.main()
