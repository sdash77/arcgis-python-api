"""
This resource provides information about the data holdings of the
server. This information is used by ArcGIS for Desktop and other
clients to validate data paths referenced by GIS services.
You can register new data items with the server by using the
Register Data Item operation. Use the Find Data Items operation to
search through the hierarchy of data items.
The Compute Ref Count operation counts and lists all references to a
specific data item. This operation helps you determine if a
particular data item can be safely deleted or refreshed.
"""
from __future__ import absolute_import
import os
import re
import json
from .._common import BaseServer
########################################################################
class DataStoreManager(BaseServer):
    """
       This resource provides information about the data holdings of the
       server. This information is used by ArcGIS for Desktop and other
       clients to validate data paths referenced by GIS services.
       You can register new data items with the server by using the
       Register Data Item operation. Use the Find Data Items operation to
       search through the hierarchy of data items.
       The Compute Ref Count operation counts and lists all references to a
       specific data item. This operation helps you determine if a
       particular data item can be safely deleted or refreshed.
    """
    _con = None
    _json_dict = None
    _url = None
    _json = None
    _gis = None
    _datastores = None
    #----------------------------------------------------------------------
    def __init__(self,
                 url,
                 gis=None,
                 connection=None):
        """Constructor
            Inputs:
               url - admin url
               gis - gis object
               connection - connection object
               initialize - optional initializes the componenents in the class
        """
        initialize = False
        super(DataStoreManager, self).__init__(
            gis=gis,
            connection=connection,
            url=url)
        if gis:
            self._con = gis._con
        if connection:
            self._con = connection
        self._url = url
        if initialize:
            self.init()
    #----------------------------------------------------------------------
    def refresh(self):
        """refreshes the DataStoreManager Object"""
        self._datastores = None
    #----------------------------------------------------------------------
    def init(self, connection=None):
        """override initialize function"""
        self._json_dict = {}
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s for %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s for %s>' % (type(self).__name__, self._url)
    @property
    def datastores(self):
        """returns a list of datastore objects"""
        if self._datastores is None:
            self._datastores = []
            for item in self.items['rootItems']:
                for path in self.search(parent_path=item)['items']:
                    self._datastores.append(Datastore(datastore=self,
                                                      path=path['path'],
                                                      datadict=None))
        return self._datastores
    #----------------------------------------------------------------------
    @property
    def config(self):
        """
           The data store configuration properties affect the behavior of
           the data holdings of the server. The properties include:
           blockDataCopy - When this property is false, or not set at all,
           copying data to the site when publishing services from a client
           application is allowed. This is the default behavior. When this
           property is true, the client application is not allowed to copy
           data to the site when publishing. Rather, the publisher is
           required to register data items through which the service being
           published can reference data. Values: true | false
        """
        params = {
            "f" : "json"
        }
        url = self._url + "/config"
        return self._con.get(path=url, params=params)
    #----------------------------------------------------------------------
    @config.setter
    def config(self, config):
        """
           This operation allows you to update the data store configuration
           You can use this to allow or block the automatic copying of data
           to the server at publish time
           Input:
              config - the JSON object containing the data
                       configuration
           Output:
              JSON message as dictionary
        """
        if config is None:
            config = {}
        params = {
            "f" : "json",
            "datastoreConfig" : config
        }
        url = self._url + "/config/update"
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def get(self, path):
        """ Returns the data item object at the given path

        Arguments
            :path: required string, the data item path
        :return:
            None if the data item is not found at that path and the data
            item object if its found
        """
        if path[0] != "/":
            path = "/%s" % path
        params = {"f" : "json"}
        urlpath = self._url + "/items" + path

        datadict = self._con.post(urlpath, params)
        if 'status' not in datadict:
            return Datastore(self, "/items" + path, datadict)
        else:
            return None
    #----------------------------------------------------------------------
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
        res = self._register_data_item(item=item)
        if res['status'] == 'success' or res['status'] == 'exists':
            return Datastore(self, "/fileShares/" + name)
        else:
            return None
        return
    #----------------------------------------------------------------------
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
        res = self._register_data_item(item=item)
        if res['status'] == 'success' or res['status'] == 'exists':
            return Datastore(self, "/enterpriseDatabases/" + name)
        else:
            #print(str(res))
            return None
    #----------------------------------------------------------------------
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
        pattern = r'\\\\[a-zA-Z]+'
        if re.match(pattern, server_path) is not None:  # starts with double backslash, double the backslashes
            server_path = server_path.replace('\\', '\\\\')

        path_str = '{"path":"' + server_path + '"}'
        params = {
            'f': 'json',
            'item' : json.dumps({
                "path": "/bigDataFileShares/" + name,
                "type": "bigDataFileShare",

                "info": {
                    "connectionString": path_str,
                    "connectionType": "fileShare"
                }
            })
        }
        res = self._register_data_item(item=params)

        if res['status'] == 'success' or res['status'] == 'exists':
            output = Datastore(self, "/bigDataFileShares/" + name)
        return output
    #----------------------------------------------------------------------
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
        res = self._register_data_item(item=item)
        if res['status'] == 'success' or res['status'] == 'exists':
            return Datastore(self, "/enterpriseDatabases/" + name)
        else:
            return None
        return
    #----------------------------------------------------------------------
    def get_total_refcount(self, path):
        """
           Computes the total number of references to a given data item
           that exist on the server. You can use this operation to
           determine if a data resource can be safely deleted (or taken
           down for maintenance).
           Input:
              path - The complete hierarchical path to the item
           Output:
              JSON message as dictionary
        """
        url = self._url + "/computeTotalRefCount"
        params = {
            "f" : "json",
            "path" : path
        }
        return self._con.post(path=url,
                              postdata=params)

    #----------------------------------------------------------------------
    def make_datastore_machine_primary(self,
                                       item_name,
                                       machine_name):
        """
        Promotes a standby machine to the primary Data Store machine. The
        existing primary machine is downgraded to a standby machine.

        Parameters:
         :item_name: name of the data store item
         :machine_name: name of the machine to promote to primary
        """
        url = self._url + "/items/enterpriseDatabases" + \
            "/{datastoreitem}/machines/{machine_name}/makePrimary".format(
                datastoreitem=item_name,
                machine_name=machine_name)
        params = {"f" : "json"}

        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def get_relational_datastore_type(self, type_id):
        """
        This resource lists the properties of a registered relational data
        store type. The properties returned are those that client
        applications must provide when creating a Relational Database
        Connection portal item.

        Parameters:
         :type_id: datastore type id
        """
        params = {"f" : "json"}
        url = self._url + "/relationalDatastoreTypes/{i}".format(
            i=type_id)
        return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    @property
    def relational_datastore_types(self):
        """
        This resource lists the relational data store types that have been
        registered with the server. Each registered relational data store
        type has both an id and a name property, as well as an array of
        userDefinedProperties, which indicates the properties client
        applications must provide when creating a Relational Database
        Connection portal item. Only administrators can register and
        unregister a relational data store type. The following database
        platforms are supported: SAP HANA, Microsoft SQL Server and
        Teradata.
        """
        params = {"f" : "json"}
        url = self._url + "/relationalDatastoreTypes"
        return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    def search(self,
               parent_path=None,
               ancestor_path=None,
               types=None,
               id=None):
        """
           You can use this operation to search through the various data
           items registered in the server's data store.
           Inputs:
              parent_path - The path of the parent under which to find items
              ancestor_path - The path of the ancestor under which to find
                             items.
              types - A filter for the type of the items
              id - A filter to search by the ID of the item
           Output:
              dictionary
        """
        params = {
            "f" : "json",
        }
        if parent_path is not None:
            params['parentPath'] = parent_path
        if ancestor_path is not None:
            params['ancestorPath'] = ancestor_path
        if types is not None:
            params['types'] = types
        if id is not None:
            params['id'] = id
        url = self._url + "/findItems"
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def _register_data_item(self, item):
        """
           Registers a new data item with the server's data store.
           Input
              item - The JSON representing the data item.
              See http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000001s9000000
           Output:
              dictionary
        """
        params = {
            "item" : item,
            "f" : "json"
        }
        url = self._url + "/registerItem"
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    @property
    def items(self):
        """ This resource lists data items that are the root of all other
            data items in the data store.
        """
        url = self._url + "/items"
        params = {
            "f" : "json"
        }
        return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    def validate(self):
        """ validates all the items in the datastore """
        params = {
            "f" : "json"
        }
        url = self._url + "/validateAllDataItems"
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def make_primary(self, datastore_name, machine_name):
        """
        Promotes a standby machine to the primary Data Store machine. The
        existing primary machine is downgraded to a standby machine.

        """
        url = self._url + "/items/enterpriseDatabases/%s/machines/%s/makePrimary" % (datastore_name, machine_name)
        params = {
            "f" : "json"
        }
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def remove_datastore(self, item_name, machine_name):
        """
        Removes a standby machine from the Data Store. This operation is
        not supported on the primary Data Store machine.

        Inputs:
           item_name - name of the data store item
           machine_name - name of the machine to remove
        """
        url = self._url + "/items/enterpriseDatabases/%s/machines/%s/remove" % (item_name, machine_name)
        params = {
            "f" : "json"
        }
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def start_datastore(self, item_name, machine_name):
        """
        Starts the database instance running on the Data Store machine.

        Inputs:
           item_name - name of the item to start
           machine_name - name of the machine to start on
        """
        url = self._url + "/items/enterpriseDatabases/%s/machines/%s/start" % (item_name, machine_name)
        params = {
            "f": "json"
        }
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def stop_datastore(self, item_name, machine_name):
        """
        Stop the database instance running on the Data Store machine.

        Inputs:
           item_name - name of the item to stop
           machine_name - name of the machine to stop on
        """
        url = self._url + "/items/enterpriseDatabases/%s/machines/%s/stop" % (item_name,
                                                                              machine_name)
        params = {
            "f": "json"
        }
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def _unregister_data_item(self, path):
        """
        Unregisters a data item that has been previously registered with
        the server's data store.

        Inputs:
           path - path to share folder

        Example:
           path = r"/fileShares/folder_share"
           print data.unregisterDataItem(path)
        """
        url = self._url + "/unregisterItem"
        params = {
            "f" : "json",
            "itempath" : path
        }
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def validate_egdb(self, data_store_name, name):
        """
        Checks the status of ArcGIS Data Store and provides a health check
        response.

        Inputs:
           data_store_namee - name of the datastore
           name - name of the machine
        """
        url = self._url + "/items/enterpriseDatabases/%s/machines/%s/validate" % (data_store_name,
                                                                                  name)
        params = {
            "f" : "json"
        }
        return self._con.post(path=url, postdata=params)
###########################################################################
class Datastore(BaseServer):
    """
    Represents a datastore (folder, database or bigdata fileshare) within
    the GIS's data store
    """
    _path = None
    _datastore = None
    _json_dict = None
    _json = None
    _con = None
    _url = None
    def __init__(self, datastore, path, datadict=None, **kwargs):
        self._path = path

        super(Datastore, self).__init__(datastore=datastore,
                                        path=path,
                                        url=datastore._url + "%s" % path,
                                        connection=datastore._con,
                                        initialize=True,
                                        datadict=datadict)
        path = "/items%s" % path
        if datastore:
            self._con = datastore._con
        self._datastore = datastore
        self._url = "%s%s" % (datastore._url, path)
        self.init()
    #----------------------------------------------------------------------
    def __str__(self):
        state = ["   %s=%r" % (attribute, value) for (attribute, value) in self.__dict__.items()]
        return '\n'.join(state)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s title:"%s" type:"%s">' % (type(self).__name__, self._url, self.type)
    #----------------------------------------------------------------------
    @property
    def manifest(self):
        """
        The manifest resource for bigdata fileshares,
        """
        data_item_manifest_url = self._url + "/manifest"
        if data_item_manifest_url.find('/bigDataFileShares') != -1:
            params = {
                'f': 'json',
            }
            res = self._con.post(data_item_manifest_url,
                                 params,
                                 verify_cert=False)
        else:
            res = {}
        return res
    #----------------------------------------------------------------------
    @manifest.setter
    def manifest(self, value):
        """
        Updates the manifest resource for bigdata fileshares
        """
        manifest_upload_url =  self._url + '/manifest/update'
        if manifest_upload_url.find('/bigDataFileShares') != -1:
            with _tempinput(json.dumps(value)) as tempfilename:
                # Build the files list (tuples)
                files = []
                files.append(('manifest', tempfilename, os.path.basename(tempfilename)))

                postdata = {
                    'f' : 'pjson'
                }

                resp = self._.con.post(manifest_upload_url, postdata, files, verify_cert=False)
                if resp['status'] == 'success':
                    return True
                else:
                    return False
        else:
            return None
    #---------------------------------------------------------------------
    @property
    def hints(self):
        """
        This returns the hints resource for a big data file share. Hints
        are advanced parameters to control the generation of Manifest.
        """
        params = {
            'download' : True,
            'read' : True
        }
        url = self._url + "/hints"
        return self._con.get(path=url,
                             params=params)
    #---------------------------------------------------------------------
    @hints.setter
    def hints(self,
              hints):
        """
        Upload a hints file for a big data file share item. This will
        replace the existing hints file. To apply the control parameters in
        the hints file and regenerate the manifest, use the editDataItem to
        edit the big data file share (using the same data store item as
        input) which will regenerate the manifest. When a manifest is
        regenerated, it will be updated only for datasets that have hints
        and for new datasets that are added to the existing big data file
        share location.

        Parameters:
         :name: name of the big data item to update
         :hints: The hints file to be uploaded.
        """
        params = {
            "f" : "json"
        }
        files = {"hints" : hints}

        url = self._url + "/hints/update"
        if url.find('/bigDataFileShares') == -1:
            return None
        return self._con.post(path=url,
                              files=files,
                              postdata=params)
    #----------------------------------------------------------------------
    @property
    def ref_count(self):
        """
        The total number of references to this data item that exist on the
        server. You can use this property to determine if this data item
        can be safely deleted (or taken down for maintenance).
        """
        return self.totalRefCount
    #----------------------------------------------------------------------
    def delete(self):
        """
        Unregisters this data item from the data store
        """
        params = {
            "f" : "json" ,
            "itempath" : self.path,
            "force": True
        }
        path = self._datastore._url + "/unregisterItem"

        resp = self._con.post(path, params, verify_cert=False)
        if resp:
            return resp.get('success')
        else:
            return False
    #----------------------------------------------------------------------
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
        path = self._datastore._url +  "/items" + self.path +  "/edit"

        resp = self._con.post(path, params, verify_cert=False)
        if resp ['status'] == 'success':
            return True
        else:
            return False
    #----------------------------------------------------------------------
    def validate(self):
        """
        Validates that this data item's path (for file shares) or connection string (for databases)
        is accessible to every server node in the site

        Output:
              True if successful
        """
        params = {
            "f" : "json",
            "item": self._json_dict
        }
        path = self._datastore._url + "/validateDataItem"

        res = self._con.post(path, params, verify_cert=False)
        return res['status'] == 'success'
    #----------------------------------------------------------------------
    @property
    def datasets(self):
        """
        Returns the datasets in the data store (currently implemented for big data file shares.)
        """
        data_item_manifest_url = self._url + "/manifest"

        params = {
            'f': 'json'
        }
        res = self._con.post(data_item_manifest_url, params, verify_cert=False)
        try:
            return res['datasets']
        except:
            return None
