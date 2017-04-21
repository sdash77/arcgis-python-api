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
from .._common import BaseServer
########################################################################
class Data(BaseServer):
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
    #----------------------------------------------------------------------
    def __init__(self,
                 url,
                 connection,
                 initialize=False):
        """Constructor
            Inputs:
               url - admin url
               connection - connection object
               initialize - optional initializes the componenents in the class
        """
        super(Data, self).__init__(connection=connection,
                                   url=url)
        self._con = connection
        self._url = url
        if initialize:
            self.init()
    #----------------------------------------------------------------------
    def init(self, connection=None):
        """override initialize function"""
        self._json_dict = {}
    #----------------------------------------------------------------------
    @property
    def datastore_configuration(self):
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
    def update_datastore_configuration(self, config=None):
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
    def bigdata_fileshare_manifest(self, name, download=True):
        """
        This returns the manifest resource for a big data file share

        Parameters:
         :name: name of the item
         :download: Optional. This will download the manifest JSON as a
          file.
        """
        params = {"f" : 'json',
                  'download' : download}
        url = self._url + "/items/bigDataFileShares/{din}/manifest".format(din=name)
        return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    def update_bigdata_fileshare_manifest(self, name, manifest, file_data=None):
        """
        Upload a manifest for a big data file share item. This will replace
        the existing manifest for the big data file share item.

        Parameters:
         :manifest: file to be uploaded
         :file_data: update the manifest by providing the manifest as a JSON
          instead of a file.
        """
        url = self._url + "/items/bigDataFileShares/{din}/manifest/update".format(
            din=name)
        params = {
            "f" : "json",
        }
        if file_data:
            params['fileData'] = file_data
        files = {
            "manifest" : manifest
        }
        return self._con.post(path=url,
                              postdata=params,
                              files=files)
    #----------------------------------------------------------------------
    def bigdata_fileshare_hints(self,
                                name,
                                download=True,
                                read=True):
        """
        This returns the hints resource for a big data file share. Hints
        are advanced parameters to control the generation of Manifest.

        Parameters:
         :name: name of the big data item to update
         :download: optional this will download hints as a hints.dat file
         :read: optional this will return the content of the hints file in
          text/plain format
        """
        params = {
            "f" : "json",
            'download' : download,
            'read' : read
        }
        url = self._url + "/items/bigDataFileShares/{din}/hints".format(
            din=name)
        return self._con.get(path=url,
                             params=params)
    #---------------------------------------------------------------------
    def update_big_data_file_sharehints(self,
                                        name,
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
        url = self._url + "/items/bigDataFileShares/{din}/hints/update".format(
            din=name)
        return self._con.post(path=url,
                              files=files,
                              postdata=params)
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
    def edit_data_item(self, item_type, name, item):
        """
        Edit an existing dataItem to update its connection information.

        Parameters:
         :dateItemType: item type
         :name: the name of the item
         :item: The JSON representing the data item.
        """
        url = self._url + "/{itemtype}/{itemname}/edit".format(
            itemtype=item_type, itemname=name)
        params = {
            "f" : "json",
            "item" : item
        }
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def edit_relational_datastore_type(self,
                                       relational_type_name,
                                       datastore_type):
        """
        Edit a registered relational data store type to update its
        properties. Before proceeding with any edit, make a backup copy of
        the type's JSON.
        **note**
        The JSON is submitted to the Edit operation URL as a value for a
        parameter named type.

        Paramters:
         :relational_type_name: relational datastore type name
         :datastore_type: The JSON object representing the relational data store type
        """
        url = "{u}/relationalDatastoreTypes/{r}/edit".format(u=self._url,
                                                             r=relational_type_name)
        params = {
            "f" : "json",
            "type" : datastore_type
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
    def find_data_items(self, parent_path=None, ancestor_path=None,
                        types=None, itemid=None):
        """
           You can use this operation to search through the various data
           items registered in the server's data store.
           Inputs:
              parent_path - The path of the parent under which to find items
              ancestor_path - The path of the ancestor under which to find
                             items.
              types - A filter for the type of the items
              itemid - A filter to search by the ID of the item
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
            params['id'] = itemid
        url = self._url + "/findItems"
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def register_data_item(self, item):
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
    def root_data_items(self):
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
    def validate_all_dataitems(self):
        """ validates all the items in the datastore """
        params = {
            "f" : "json"
        }
        url = self._url + "/validateAllDataItems"
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def validate_data_item(self, item):
        """
           In order for a data item to be registered and used successfully
           within the server's data store, you need to make sure that the
           path (for file shares) or connection string (for databases) is
           accessible to every server node in the site. This can be done by
           invoking the Validate Data Item operation on the JSON object
           representing the data store.
           Validating a data item does not automatically register it for
           you. You need to explicitly register your data item by invoking
           the Register Data Item operation.
           Input:
              item - The JSON representing the data item.
           Output:
              dictionary
        """
        params = {
            "f" : "json",
            "item" : item
        }
        url = self._url + "/validateDataItem"
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
    def unregister_data_item(self, path):
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
    def validate_datastore(self, data_store_name, name):
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
