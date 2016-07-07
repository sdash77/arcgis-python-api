"""
Contains all items relating to the datastore
"""
import os
import json
from ._util import _tempinput

class DatastoreManager(object):
    """
    Manager class for managing the GIS data stores in on-premises ArcGIS Portals.
    This class is not created by users directly.
    An instance of this class, called 'datastores', is available as a property of the GIS object.
    Users call methods on this 'datastores' object to manage the data stores.
    """
    def __init__(self, gis, admin_url=None):
        self._gis = gis
        self._portal = gis._portal
        if admin_url is None:
            fedservers_url = self._gis._url + "portaladmin/federation/servers?f=json"
            res = self._gis._portal.con.get(fedservers_url)
            servers = res['servers']

            self._admin_url = None

            for server in servers:
                if server['isHosted']:
                    self._admin_url = server['adminUrl'] + '/admin'
        else:
            self._admin_url = admin_url

    def __str__(self):
        return json.dumps(self)

    @property
    def config(self):
        """
        The data store configuration properties affect the behavior of the data holdings of the server. The properties include:
        blockDataCopy—When this property is False, or not set at all, copying data to the site when publishing services from a client application is allowed. This is the default behavior.
        When this property is True, the client application is not allowed to copy data to the site when publishing. Rather, the publisher is required to register data items through which the service being published can reference data. Values: True | False
        Note:
        If you specify the property as True, users will not be able to publish geoprocessing services and geocode services from composite locators. These service types require data to be copied to the server. As a workaround, you can temporarily set the property to False, publish the service, and then set the property back to True.
        """
        params = {"f" : "json"}
        path = self._admin_url + "/data/config"
        res = self._portal.con.post(path, params)
        return res

    @config.setter
    def config(self, value):
        """
        The data store configuration properties affect the behavior of the data holdings of the server. The properties include:
        blockDataCopy—When this property is False, or not set at all, copying data to the site when publishing services from a client application is allowed. This is the default behavior.
        When this property is True, the client application is not allowed to copy data to the site when publishing. Rather, the publisher is required to register data items through which the service being published can reference data. Values: True | False
        Note:
        If you specify the property as True, users will not be able to publish geoprocessing services and geocode services from composite locators. These service types require data to be copied to the server. As a workaround, you can temporarily set the property to False, publish the service, and then set the property back to True.
        """
        params = {"f" : "json"}
        params['datastoreConfig'] = value
        path = self._admin_url + "/data/config/update"
        res = self._portal.con.post(path, params)
        return res

    def add_folder(self,
                   name,
                   server_path,
                   client_path=None):
        """
        Registers a folder with the data store.
        Input
            name - unique fileshare name on the server
            server_path - the path to the folder from the server (and client, if shared path)
            client_path - if folder is replicated, the path to the folder from the client
            if folder is shared, don't set this parameter
        Output:
              the data item is registered successfully, None otherwise
        """
        conn_type = "shared"
        if client_path is not None:
            conn_type = "replicated"

        item = {
            "type" : "folder",
            "path" : "/fileShares/" + name,
            "info" : {
                "path" : server_path,
                "dataStoreConnectionType" : conn_type
            }
        }

        if client_path is not None:
            item['clientPath'] = client_path

        params = {
            "f" : "json",
            "item" : item
        }
        path = self._admin_url + "/data/registerItem"
        res = self._portal.con.post(path, params)
        if res['status'] == 'success' or res['status'] == 'exists':
            return DatastoreItem(self, "/fileShares/" + name)
        else:
            print(str(res))
            return None

    def add_bigdata(self,
                    name,
                    server_path=None):
        """
        Registers a bigdata fileshare with the data store.
        Input
            name - unique bigdata fileshare name on the server
            server_path - the path to the folder from the server
        Output:
              the data item if registered successfully, None otherwise
        """
        output = None
        path = self._admin_url + "/data/registerItem"

        params = {
            'f': 'json',
            'item' : {
                "path": "/bigDataFileShares/" + name,
                "type": "bigDataFileShare",
                "id": "",
                "info": {
                    "path" : server_path
                }
            }
        }
        res = self._portal.con.post(path, params)

        if res['status'] == 'success' or res['status'] == 'exists':
            output = DatastoreItem(self, "/bigDataFileShares/" + name)

        if res['success']:
            print("Created Big Data file share for " + name)
        elif res['status'] == 'exists':
            print("Big Data file share exists for " + name)

        return output

    def add_database(self,
                     name,
                     conn_str,
                     client_conn_str=None,
                     conn_type="shared"):
        """
        Registers a database with the data store.
        Input
            name - unique database name on the server
            conn_str - the path to the folder from the server (and client, if shared or serverOnly database)
            client_conn_str: connection string for client to connect to replicated enterprise database>
            conn_type - "<shared|replicated|serverOnly>"
        Output:
            the data item is registered successfully, None otherwise
        """

        item = {
            "type" : "egdb",
            "path" : "/enterpriseDatabases/" + name,
            "info" : {
                "connectionString" : conn_str,
                "dataStoreConnectionType" : conn_type
            }
        }

        if client_conn_str is not None:
            item['info']['clientConnectionString'] = client_conn_str

        is_managed = False
        if conn_type == "serverOnly":
            is_managed = True

        item['info']['isManaged'] = is_managed

        params = {
            "f" : "json",
            "item" : item
        }
        path = self._admin_url + "/data/registerItem"
        res = self._portal.con.post(path, params)
        if res['status'] == 'success' or res['status'] == 'exists':
            return DatastoreItem(self, "/enterpriseDatabases/" + name)
        else:
            print(str(res))
            return None

    def add(self,
            name,
            item):
        """
        Registers a new data item with the data store.
        Input
            item - The disct representing the data item.
            See http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000001s9000000
        Output:
              True if the data item is registered successfully, False otherwise
        """
        params = {
            "f" : "json"
        }

        params['item'] = item

        path = self._admin_url + "/data/registerItem"
        res = self._portal.con.post(path, params)
        if res['status'] == 'success' or res['status'] == 'exists':
            return DatastoreItem(self, "/enterpriseDatabases/" + name)
        else:
            print(str(res))
            return None

    def get(self, path):
        """ Returns the data item object at the given path

        Arguments
            path        required string, the data item path
        :return:
            None if the data item is not found at that path and the data item object if its found
        """
        params = { "f" : "json" }
        urlpath = self._admin_url + "/data/items" + path

        datadict = self._portal.con.post(urlpath, params)
        if 'status' not in datadict:
            return DatastoreItem(self, path)
        else:
            print(datadict['messages'])
            return None

    def search(self, parent_path=None, ancestor_path=None,
               types=None, id=None):
        """
           You can use this operation to search through the various data
           items registered in the server's data store. Searching without specifying the parent_path and other parameters returns a lists of all registered data items
           Inputs:
              parentPath - The path of the parent under which to find items. To get the root data items, pass '/'
              ancestorPath - The path of the ancestor under which to find
                             items.
              types - A comma separated filter for the type of the items. Types include folder, egdb, bigDataFileShare, datadir
              id - A filter to search by the ID of the item

            :return:
            Returns a list of data items matching the specified query
        """
        params = {
            "f" : "json",
        }
        if parent_path is None and ancestor_path is None and types is None and id is None:
            ancestor_path = '/'
        if parent_path is not None:
            params['parentPath'] = parent_path
        if ancestor_path is not None:
            params['ancestorPath'] = ancestor_path
        if types is not None:
            params['types'] = types
        if id is not None:
            params['id'] = id


        path = self._admin_url + "/data/findItems"


        dataitems = []

        res = self._portal.con.post(path, params)
        for item in res['items']:
            dataitems.append(DatastoreItem(self, item['path']))
        return dataitems

    def validate(self):
        """
        Validates all items in the datastore and returns True if validated.

        In order for a data item to be registered and used successfully within the GIS's data store,
        you need to make sure that the path (for file shares) or connection string (for databases)
        is accessible to every server node in the site. To validate all registered data items all
        at once, you can invoke this operation.
        """
        params = {"f" : "json"}
        path = self._admin_url + "/data/validateAllDataItems"
        res = self._portal.con.post(path, params)
        return res['status'] == 'success'

class DatastoreItem(dict):
    """
    Represents a datastore item (folder, database or bigdata fileshare) within the GIS's data store
    """
    def __init__(self, datastore, path):
        dict.__init__(self)
        self._datastore = datastore
        self._portal = datastore._portal
        self._admin_url = datastore._admin_url

        self.datapath = path


        params = { "f" : "json" }
        path = self._admin_url + "/data/items" + self.datapath

        datadict = self._portal.con.post(path, params)

        if datadict:
            self.__dict__.update(datadict)
            dict.update(datadict)

    def __getattr__(self, name): # support group attributes as group.access, group.owner, group.phone etc
        return dict.__getitem__(self, name)

    def __getitem__(self, k): # support group attributes as dictionary keys on this object, eg. group['owner']
        try:
            return dict.__getitem__(self, k)
        except KeyError:
            params = { "f" : "json" }
            path = self._admin_url + "/data/items" + self.datapath

            datadict = self._portal.con.post(path, params)
            super(DatastoreItem, self).update(datadict)
            self.__dict__.update(datadict)
            return dict.__getitem__(self, k)

    def __str__(self):
        state = ["   %s=%r" % (attribute, value) for (attribute, value) in self.__dict__.items()]
        return '\n'.join(state)

    def __repr__(self):
        return '<%s title:"%s" type:"%s">' % (type(self).__name__, self.path, self.type)

    @property
    def manifest(self):
        """
        The manifest resource for bigdata fileshares,
        """
        data_item_manifest_url = self._admin_url + '/data/items' + self.datapath + "/manifest"

        params = {
            'f': 'json',
        }
        res = self._portal.con.post(data_item_manifest_url, params)
        return res

    @manifest.setter
    def manifest(self, value):
        """
        Updates the manifest resource for bigdata fileshares,
        """
        manifest_upload_url =  self._admin_url + '/data/items' + self.datapath + '/manifest/update'

        with _tempinput(json.dumps(value)) as tempfilename:
            # Build the files list (tuples)
            files = []
            files.append(('manifest', tempfilename, os.path.basename(tempfilename)))

            postdata = {
                'f' : 'pjson'
            }

            resp = self._portal.con.post(manifest_upload_url, postdata, files)

            if resp['status'] == 'success':
                return True
            else:
                print(str(resp))
                return False

    @property
    def ref_count(self):
        """
        The total number of references to this data item that exist on the server. You can use this property to determine if this data item can be safely deleted (or taken down for maintenance).
        """
        data_item_manifest_url = self._admin_url + '/data/computeTotalRefCount'

        params = {
            'f': 'json',
            'itemPath': self.datapath
        }
        res = self._portal.con.post(data_item_manifest_url, params)
        return res["totalRefCount"]

    def delete(self):
        """
        Unregisters this data item from the data store
        """
        params = {
            "f" : "json" ,
            "itempath" : self.datapath,
            "force": True
        }
        path = self._admin_url + "/data/unregisterItem"

        resp = self._portal.con.post(path, params)
        if resp:
            return resp.get('success')
        else:
            return False

    def update(self, item):
        """
        Edits this data item to update its connection information.

        Input
            item - the dict representation of the updated item
        Output:
              True if successful
        """
        params = {
            "f" : "json" ,
            "item" : item
        }
        path = self._admin_url +  "/data/items" + self.datapath +  "/edit"

        resp = self._portal.con.post(path, params)
        if resp ['status'] == 'success':
            return True
        else:
            return False

    def validate(self):
        """
        Validates that this data item's path (for file shares) or connection string (for databases)
        is accessible to every server node in the site

        Output:
              True if successful
        """
        params = { "f" : "json" }
        path = self._admin_url + "/data/items" + self.datapath

        datadict = self._portal.con.post(path, params)

        params = {
            "f" : "json",
            "item": datadict
        }
        path = self._admin_url + "/data/validateDataItem"

        res = self._portal.con.post(path, params)
        return res['status'] == 'success'

    def list_datasets(self):
        """
        Lists the datasets in a big data file share.
        """
        data_item_manifest_url = self._admin_url + '/data/items' + self.datapath + "/manifest"

        params = {
            'f': 'json',
        }
        res = self._portal.con.post(data_item_manifest_url, params)

        for dataset in res['datasets']:
            print("/server/datastores" + self.datapath + '/' + dataset['path'] + ' ('+ dataset['type'] + ')')

