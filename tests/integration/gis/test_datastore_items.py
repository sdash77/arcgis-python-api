import os
import sys
#sys.path.insert(0, r"C:\SVN\achapkowski_geosaurus_fork_issue3686\src")
import json
import uuid
import unittest
import pytest

import arcgis
from arcgis.gis import GIS
from arcgis.gis._impl._datastores import PortalDataStore
from arcgis.gis._impl._jb import StatusJob

try:
    gis = GIS(url="https://pyrite.esri.com/portal",
              username="admin",
              password="esri.agp",
              verify_cert=False)
    SKIPTEST = False
except:
    SKIPTEST = True

@unittest.skipIf(SKIPTEST, "Could not connect to test server")
class TestPortalDataStore1081(unittest.TestCase):
    """
    Tests the 10.7/10.7.1/10.8.1 functionality for Portal Datastores
    
    These tests focus primarily on scene package layers and bulk publishing of layers
    """
    #----------------------------------------------------------------------
    def test_validate(self):
        """tests the validate operation on portal"""
        server_list = gis.admin.federation.servers
        server_id = server_list['servers'][0]['id']                
        h = uuid.uuid4().hex[:5]
        info = {"info":{"isManaged":False,"dataStoreConnectionType":"replicated",
                        "path":"\\\\kyanite\\packages"},
                "type":"folder","path":"/fileShares/ajc_folder_test",
                "clientPath":"\\\\kyanite\\packages"}
        txt = json.dumps(info)
        item = gis.content.add(
            {
            'title' : f'datastore_{h}',
            'type' : "Data Store",
            'tags' : "erase me",
            'text' : txt
            })
        assert gis.datastore.register(item=item, server_id=server_id)
        assert gis.datastore.servers(item=item.itemid)        
        ds_item = item.itemid
        server_id = server_id
        assert gis.datastore.validate(server_id=server_id, item=ds_item)
        ds_item = gis.content.get(ds_item)
        assert gis.datastore.validate(server_id=server_id, item=ds_item)
    #----------------------------------------------------------------------
    
    def test_servers(self):
        """tests the server method"""
        server_list = gis.admin.federation.servers
        server_id = server_list['servers'][0]['id']                
        h = uuid.uuid4().hex[:5]
        info = {"info":{"isManaged":False,"dataStoreConnectionType":"replicated",
                        "path":"\\\\kyanite\\packages"},
                "type":"folder","path":"/fileShares/ajc_folder_test",
                "clientPath":"\\\\kyanite\\packages"}
        txt = json.dumps(info)
        item = gis.content.add(
            {
            'title' : f'datastore_{h}',
            'type' : "Data Store",
            'tags' : "erase me",
            'text' : txt
            })
        assert gis.datastore.register(item=item, server_id=server_id)
        assert gis.datastore.servers(item=item.itemid)
        assert isinstance(gis.datastore.servers(item=item.itemid), list)        
        assert gis.datastore.unregister(item=item, server_id=server_id)
        assert item.delete()        
        
    #----------------------------------------------------------------------
    def test_layers(self):
        """tests that layers for the datastore are returned as a list"""
        server_list = gis.admin.federation.servers
        server_id = server_list['servers'][0]['id']                
        h = uuid.uuid4().hex[:5]
        info = {"info":{"isManaged":False,"dataStoreConnectionType":"replicated",
                        "path":"\\\\kyanite\\packages"},
                "type":"folder","path":"/fileShares/ajc_folder_test",
                "clientPath":"\\\\kyanite\\packages"}
        txt = json.dumps(info)
        item = gis.content.add(
            {
            'title' : f'datastore_{h}',
            'type' : "Data Store",
            'tags' : "erase me",
            'text' : txt
            })
        assert gis.datastore.register(item=item, server_id=server_id)
               
        layers = gis.datastore.layers(item=item.itemid)
        assert isinstance(layers, list)
        assert gis.datastore.unregister(item=item, server_id=server_id)
        assert item.delete()         
        gis.datastore.properties
    #----------------------------------------------------------------------
    def test_datastore_root(self):
        """tests the datastore root properties"""
        assert gis.datastore.properties
        assert gis.datastore._all_datasets # not used publicly
        assert isinstance(gis.datastore, PortalDataStore)
    #----------------------------------------------------------------------
    def test_register_unregister_operations(self):
        """tests the unregister/register operation"""
        server_list = gis.admin.federation.servers
        server_id = server_list['servers'][0]['id']                
        h = uuid.uuid4().hex[:5]
        info = {"info":{"isManaged":False,"dataStoreConnectionType":"replicated",
                        "path":"\\\\kyanite\\packages"},
                "type":"folder","path":"/fileShares/ajc_folder_test",
                "clientPath":"\\\\kyanite\\packages"}
        txt = json.dumps(info)
        item = gis.content.add(
            {
            'title' : f'datastore_{h}',
            'type' : "Data Store",
            'tags' : "erase me",
            'text' : txt
            })
        assert gis.datastore.register(item=item, server_id=server_id)
        assert gis.datastore.unregister(item=item, server_id=server_id)
        assert item.delete()
    #----------------------------------------------------------------------
    @unittest.skip("need stable egdb")
    def test_publish_delete_layers(self):
        """tests the publish/delete all layers operations"""
        server_list = gis.admin.federation.servers
        server_id = server_list['servers'][0]['id']        
        for item in gis.content.search("datastore_"):
            gis.datastore.unregister(item=item, server_id=server_id)
            item.delete()
        network_path = r"\\datalibrary\data\Earth\Europe\Austria\Salzburg\City of Salzburg"
        h = uuid.uuid4().hex[:5]
        info = {"info":{"isManaged":False,"dataStoreConnectionType":"replicated",
                        "path": network_path},
                "type":"folder","path": f"/fileShares/ajc_folder_{h}",
                "clientPath": network_path }
        txt = json.dumps(info)
        item = gis.content.add(
            {
            'title' : f'datastore_{h}',
            'type' : "Data Store",
            'tags' : "erase me",
            'text' : txt
            })
        try:
            cfg = json.loads("""{"serviceName":"%s","type":"MapServer","capabilities":"Map","extensions":[{"typeName":"FeatureServer","capabilities":"Query","enabled":"true","properties":{"maxRecordCount":"3500"}}]}""" % uuid.uuid4().hex[:5])
            assert gis.datastore.register(item=item, server_id=server_id)  
            g = gis.datastore.publish_layers(item=item, srv_config=cfg, server_id=server_id)  
            r = gis.datastore.delete_layers(item=item)
        except Exception as e:
            print(e)
            raise e
        finally:
            gis.datastore.unregister(item=item, server_id=server_id)
            item.delete()
    #----------------------------------------------------------------------
    def test_publish(self):
        """
        Tests the publishing of a single layer on Portal.
        """
        try:
            
            h = uuid.uuid4().hex[:5]
            info = {"info":{"isManaged":False,"dataStoreConnectionType":"replicated",
                            "path":"\\\\kyanite\\packages"},
                    "type":"folder","path": f"/fileShares/ajc_folder_{h}",
                    "clientPath":"\\\\kyanite\\packages"}
            txt = json.dumps(info)
            ds_item = gis.content.add(
                {
                'title' : f'datastore_{h}',
                'type' : "Data Store",
                'tags' : "erase me",
                'text' : txt
                })            
            # gets list of servers and their ids
            server_list = gis.admin.federation.servers
            server_id = server_list['servers'][0]['id']
            
            # register data store
            gis.datastore.register(ds_item, server_id)
            
            # query datastore for list of datasets
            datastore_id = ds_item.get_data()['id']
            datasets = gis.datastore.describe(ds_item, server_id=server_id, path="/", store_type='datastore').result()
            
            if not 'result' in datasets:
                datasets = gis.datastore.describe(ds_item, server_id=server_id, path="/", store_type='datastore').result()
            dataset_path = datasets['result']['children'][0]['path']
            
            # publish the scene layer
            service_config = { "type": "SceneServer", 
                               "serviceName": f"SanFran{h}",
                               "properties": {"pathInCachedStore":dataset_path,"cacheStoreId":datastore_id}
                                }

            sl_item = gis.datastore.publish(config=service_config, server_id=server_id,  folder=None,
                                             description='test', tags=['test'])
            assert isinstance(sl_item.result(), list)
            assert all([isinstance(i, arcgis.gis.Item) for i in sl_item.result()])
            [i.delete() for i in sl_item.result()]
        except Exception as e:
            print(e)
            raise e
        finally:
            gis.datastore.unregister(item=ds_item, server_id=server_id)
            try:
                ds_item.delete()
            except:
                pass
    #----------------------------------------------------------------------
    def test_describe(self):
        """
        tests the describe asynchronous method
        """
        try:
            server_list = gis.admin.federation.servers
            server_id = server_list['servers'][0]['id']
            network_path = r"\\datalibrary\data\Earth\Europe\Austria\Salzburg\City of Salzburg"
            h = uuid.uuid4().hex[:5]
            info = {"info":{"isManaged":False,"dataStoreConnectionType":"replicated",
                            "path": network_path},
                    "type":"folder","path": f"/fileShares/ajc_folder_{h}",
                    "clientPath": network_path }
            txt = json.dumps(info)
            item = gis.content.add(
                {
                'title' : f'datastore_{h}',
                'type' : "Data Store",
                'tags' : "erase me",
                'text' : txt
                })
            assert gis.datastore.register(item=item, server_id=server_id)
            j = gis.datastore.describe(item, server_id=server_id, path="/", store_type='datastore')
            assert j
            assert isinstance(j, StatusJob)
            assert j.result()
        except Exception as e:
            print(e)
            raise e
        finally:
            gis.datastore.unregister(item=item, server_id=server_id)
            item.delete()
    
if __name__ == "__main__":
    unittest.main()
