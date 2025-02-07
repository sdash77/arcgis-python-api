import uuid
import unittest
from arcgis.gis import ContentManager, Item
from arcgis.gis._impl._datastores import PortalDataStore
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging

enable_verbose_logging()


@integration_test
@profiles.admin_enterprise
class TestBulkPublishing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = cls.gis.content.folders._get_or_create("integration_testing")
        cls.item: Item = folder.add(
            item_properties={
                "text": {
                    'info': {
                        'isManaged': False,
                        'dataStoreConnectionType': 'shared',
                        'connectionString': 'ENCRYPTED_PASSWORD_UTF8=00022e6851614f4e534d78584b7a4265794f63626c5443435474315044496d594871465877596a78734c507a7638493d2a00;ENCRYPTED_PASSWORD=00022e685a61446e495a5637556c4b325251746847634a444d4c596b446178346e4b55577445735955664561336d733d2a00;SERVER=andradej;INSTANCE=sde:sqlserver:andradej;DBCLIENT=sqlserver;DB_CONNECTION_PROPERTIES=andradej;DATABASE=sashadb;USER=sasha;VERSION=sde.DEFAULT;AUTHENTICATION_MODE=DBMS',
                    },
                    'type': 'egdb',
                    'path': '/enterpriseDatabases/bulk_publish_test_db',
                },
                "type": "Data Store",
                "title": f"bulk_publish_{uuid.uuid4().hex[:4]}",
            }
        ).result()
        cls.dstore: PortalDataStore = cls.gis.datastore

        # servers:dict = cls.gis.servers
        server_id: str = [
            server
            for server in cls.gis.servers['servers']
            if server['isHosted']
        ][0]['id']
        cls.server_id: str = server_id
        status = cls.dstore.register(cls.item, server_id, bind=False)
        assert status

    def test_bulk_publish_workflow(self):
        """tests the publish and deleting of the layers"""
        assert self.dstore.validate(server_id=self.server_id, item=self.item)
        cm: ContentManager = self.gis.content
        folder = cm.folders.create(
            folder=f"bulk_publish_{uuid.uuid4().hex[:4]}"
        ).properties.get("id")

        srv_config = {
            'type': 'MapServer',
            'capabilities': 'Map,Query,Data',
            'properties': {
                'datesInUnknownTimeZone': False,
                'dateFieldsTimezoneID': 'Pacific Standard Time',
                'dateFieldsRespectsDayLightSavingTime': True,
            },
            'extensions': [
                {
                    'typeName': 'FeatureServer',
                    'capabilities': 'Query',
                    'enabled': 'true',
                    'properties': {'maxRecordCount': '4000'},
                }
            ],
        }
        publish_results = self.dstore.publish_layers(
            item=self.item,
            srv_config=srv_config,
            server_id=self.server_id,
            folder=folder,
            server_folder=f"bulk_publish_{uuid.uuid4().hex[:4]}",
        )
        layers = self.dstore.layers(self.item)
        assert isinstance(layers, list)
        assert self.dstore.refresh_server(
            item=self.item, server_id=self.server_id
        )

        assert self.dstore.delete_layers(item=self.item)
        assert self.dstore.unregister(
            item=self.item, server_id=self.server_id
        )
        assert self.item.delete()
        assert cm.delete_folder(folder)


if __name__ == "__main__":
    unittest.main()
