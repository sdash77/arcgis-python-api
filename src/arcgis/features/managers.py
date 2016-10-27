"""
Helper classes for managing feature layers and datasets.  These class are not created by users directly.
Instances of this class, are available as a properties of feature layers and make it easier to manage them.
"""

import collections
import json
import tempfile

from arcgis._impl.common._mixins import PropertyMap
from arcgis.gis import _GISResource


#pylint: disable=protected-access

class AttachmentManager(object):
    """
    Manager class for manipulating feature layer attachments. This class is not created by users directly.
    An instance of this class, called 'attachments', is available as a property of the FeatureLayer object,
    if the layer supports attachments.
    Users call methods on this 'attachments' object to manipulate (create, get, list, delete) attachments.
    """

    def __init__(self, layer):
        self._layer = layer

    def get_list(self, oid):
        """ returns the list of attachements for a given OBJECT ID """
        return self._layer._list_attachments(oid)['attachmentInfos']

    def download(self, oid, attachment_id, save_path=None):
        """ downloads attachment and returns it's path on disk """
        att_path = '{}/{}/attachments/{}'.format(self._layer.url, oid, attachment_id)
        if not save_path:
            save_path = tempfile.gettempdir()
        return self._layer._con.get(path=att_path, try_json=False, out_folder=save_path, token=self._layer._token)

    def add(self, oid, file_path):
        """ Adds an attachment to a feature layer
            Input:
              oid - string - OBJECTID value to add attachment to
              file_path - string - path to file
            Output:
              JSON Repsonse
        """
        return self._layer._add_attachment(oid, file_path)

    def delete(self, oid, attachment_id):
        """ removes an attachment from a feature
            Input:
              oid - integer or string - id of feature
              attachment_id - integer - id of attachment to erase
            Output:
               JSON response
        """
        return self._layer._delete_attachment(oid, attachment_id)

    def update(self, oid, attachment_id, file_path):
        """ updates an existing attachment with a new file
            Inputs:
               oid - string/integer - Unique record ID
               attachment_id - integer - Unique attachment identifier
               file_path - string - path to new attachment
            Output:
               JSON response
        """
        return self._layer._update_attachment(oid, attachment_id, file_path)


class ReplicaManager(object):
    """
    Manager class for manipulating replicas for disconnected editing of feature layer collections.
    This class is not created by users directly.
    An instance of this class, called 'replicas', is available as a property of the FeatureLayerCollection object,
    if the layer is sync enabled / supports disconnected editing.
    Users call methods on this 'replicas' object to manipulate (create, synchronize, unregister) replicas.
    """

    def __init__(self, featsvc):
        self._fs = featsvc

    def get_list(self):
        """ returns all the replicas for the feature layer collection """
        return self._fs._replicas

    # ----------------------------------------------------------------------
    def unregister(self, replica_id):
        """
           unregisters a replica from a feature layer collection
           Inputs:
             replica_id - The replicaID returned by the feature service
                          when the replica was created.
        """
        return self._fs._unregister_replica(replica_id)

    # ----------------------------------------------------------------------
    def get(self, replica_id):
        """
           returns replica metadata for a specific replica.
           Inputs:
              replica_id - The replicaID returned by the feature service
                           when the replica was created.
        """
        return self._fs._replica_info(replica_id)

    # ----------------------------------------------------------------------
    def create(self,
               replica_name,
               layers,
               layer_queries=None,
               geometry_filter=None,
               replica_sr=None,
               transport_type="esriTransportTypeUrl",
               return_attachments=False,
               return_attachments_databy_url=False,
               async=False,
               attachments_sync_direction="none",
               sync_model="none",
               data_format="json",
               replica_options=None,
               wait=False,
               out_path=None):
        """
        The create operation is performed on a feature layer collection
        resource. This operation creates the replica between the feature
        dataset and a client based on a client-supplied replica definition.
        It requires the Sync capability. See Sync overview for more
        information on sync. The response for create includes
        replicaID, replica generation number, and data similar to the
        response from the feature layer collection query operation.
        The create operation returns a response of type
        esriReplicaResponseTypeData, as the response has data for the
        layers in the replica. If the operation is called to register
        existing data by using replicaOptions, the response type will be
        esriReplicaResponseTypeInfo, and the response will not contain data
        for the layers in the replica.

        Inputs:
           replicaName - name of the replica
           layers - layers to export
           layerQueries - In addition to the layers and geometry parameters, the layerQueries
            parameter can be used to further define what is replicated. This
            parameter allows you to set properties on a per layer or per table
            basis. Only the properties for the layers and tables that you want
            changed from the default are required.
            Example:
             layerQueries = {"0":{"queryOption": "useFilter", "useGeometry": true,
             "where": "requires_inspection = Yes"}}
           geometryFilter - Geospatial filter applied to the replica to
            parse down data output.
           returnAttachments - If true, attachments are added to the replica and returned in the
            response. Otherwise, attachments are not included.
           returnAttachmentDatabyURL -  If true, a reference to a URL will be provided for each
            attachment returned from createReplica. Otherwise,
            attachments are embedded in the response.
           replicaSR - the spatial reference of the replica geometry.
           transportType -  The transportType represents the response format. If the
            transportType is esriTransportTypeUrl, the JSON response is contained in a file,
            and the URL link to the file is returned. Otherwise, the JSON object is returned
            directly. The default is esriTransportTypeUrl.
            If async is true, the results will always be returned as if transportType is
            esriTransportTypeUrl. If dataFormat is sqlite, the transportFormat will always be
            esriTransportTypeUrl regardless of how the parameter is set.
            Values: esriTransportTypeUrl | esriTransportTypeEmbedded
           returnAttachments - If true, attachments are added to the replica and returned in
            the response. Otherwise, attachments are not included. The default is false. This
            parameter is only applicable if the feature service has attachments.
           returnAttachmentsDatabyURL -  If true, a reference to a URL will be provided for
            each attachment returned from createReplica. Otherwise, attachments are embedded
            in the response. The default is true. This parameter is only applicable if the
            feature service has attachments and if returnAttachments is true.
           attachmentsSyncDirection - Client can specify the attachmentsSyncDirection when
            creating a replica. AttachmentsSyncDirection is currently a createReplica property
            and cannot be overridden during sync.
            Values: none, upload, bidirectional
           async - If true, the request is processed as an asynchronous job, and a URL is
            returned that a client can visit to check the status of the job. See the topic on
            asynchronous usage for more information. The default is false.
           syncModel - Client can specify the attachmentsSyncDirection when creating a replica.
            AttachmentsSyncDirection is currently a createReplica property and cannot be
            overridden during sync.
           dataFormat - The format of the replica geodatabase returned in the response. The
            default is json.
            Values: filegdb, json, sqlite, shapefile
           replicaOptions - This parameter instructs the createReplica operation to create a
            new replica based on an existing replica definition (refReplicaId). It can be used
            to specify parameters for registration of existing data for sync. The operation
            will create a replica but will not return data. The responseType returned in the
            createReplica response will be esriReplicaResponseTypeInfo.
           wait - if async, wait to pause the process until the async operation is completed.
           out_path - folder path to save the file
        """
        return self._fs._create_replica(replica_name,
                                        layers,
                                        layer_queries,
                                        geometry_filter,
                                        replica_sr,
                                        transport_type,
                                        return_attachments,
                                        return_attachments_databy_url,
                                        async,
                                        attachments_sync_direction,
                                        sync_model,
                                        data_format,
                                        replica_options,
                                        wait,
                                        out_path)

    # ----------------------------------------------------------------------
    def synchronize(self,
                    replica_id,
                    transport_type="esriTransportTypeUrl",
                    replica_server_gen=None,
                    return_ids_for_adds=False,
                    edits=None,
                    return_attachment_databy_url=False,
                    async=False,
                    sync_direction="snapshot",
                    sync_layers="perReplica",
                    edits_upload_id=None,
                    edits_upload_format=None,
                    data_format="json",
                    rollback_on_failure=True):
        """
        synchronizes replica with feature layer collection
        http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000000vv000000
        """
        # TODO:
        return self._fs._synchronize_replica(replica_id,
                                             transport_type,
                                             replica_server_gen,
                                             return_ids_for_adds,
                                             edits,
                                             return_attachment_databy_url,
                                             async,
                                             sync_direction,
                                             sync_layers,
                                             edits_upload_id,
                                             edits_upload_format,
                                             data_format,
                                             rollback_on_failure)


class FeatureLayerCollectionManager(_GISResource):
    """
    Allows updating the definition (if access permits) of a feature layer collection.
    This class is not created by users directly.
    An instance of this class, called 'manager', is available as a property of the FeatureLayerCollection object.

    Users call methods on this 'manager' object to manage the feature layer collection.
    """

    def __init__(self, url, gis=None, fs=None):
        super(FeatureLayerCollectionManager, self).__init__(url, gis)
        self._fs = fs
        self._populate_layers()

    def _populate_layers(self):
        """
        populates layers and tables in the managed feature service
        """
        layers = []
        tables = []

        try:
            for layer in self.properties.layers:
                layers.append(FeatureLayerManager(self.url + '/' + str(layer['id']), self._gis))
        except:
            pass

        try:
            for table in self.properties.tables:
                tables.append(FeatureLayerManager(self.url + '/' + str(table['id']), self._gis))
        except:
            pass

        self.layers = layers
        self.tables = tables

    # ----------------------------------------------------------------------
    def refresh(self):
        """ refreshes a feature layer collection """
        params = {"f": "json"}
        refresh_url = self._url + "/refresh"
        res = self._con.post(refresh_url, params)

        super(FeatureLayerCollectionManager, self)._refresh()
        self._populate_layers()

        self._fs._refresh()
        self._fs._populate_layers()

        return res

    # ----------------------------------------------------------------------
    def add_to_definition(self, json_dict):
        """
           The add_to_definition operation supports adding a definition
           property to a hosted feature layer collection service. The result of this
           operation is a response indicating success or failure with error
           code and description.

           This function will allow users to change add additional values
           to an already published service.

           Input:
              json_dict - part to add to host service.  The part format can
                          be derived from the properties property.  For
                          layer level modifications, run updates on each
                          individual feature service layer object.
           Output:
              JSON message as dictionary
        """
        if isinstance(json_dict, PropertyMap):
            json_dict = dict(json_dict)

        params = {
            "f": "json",
            "addToDefinition": json.dumps(json_dict),
            "async": False
        }
        adddefn_url = self._url + "/addToDefinition"
        res = self._con.post(adddefn_url, params)
        self.refresh()
        return res

    # ----------------------------------------------------------------------
    def update_definition(self, json_dict):
        """
           The update_definition operation supports updating a definition
           property in a hosted feature layer collection service. The result of this
           operation is a response indicating success or failure with error
           code and description.

           Input:
              json_dict - part to add to host service.  The part format can
                          be derived from the properties property.  For
                          layer level modifications, run updates on each
                          individual feature service layer object.
           Output:
              JSON Message as dictionary
        """
        definition = None
        if json_dict is not None:

            if isinstance(json_dict, PropertyMap):
                definition = dict(json_dict)
            if isinstance(json_dict, collections.OrderedDict):
                definition = json_dict
            else:

                definition = collections.OrderedDict()
                if 'hasStaticData' in json_dict:
                    definition['hasStaticData'] = json_dict['hasStaticData']
                if 'allowGeometryUpdates' in json_dict:
                    definition['allowGeometryUpdates'] = json_dict['allowGeometryUpdates']
                if 'capabilities' in json_dict:
                    definition['capabilities'] = json_dict['capabilities']
                if 'editorTrackingInfo' in json_dict:
                    definition['editorTrackingInfo'] = collections.OrderedDict()
                    if 'enableEditorTracking' in json_dict['editorTrackingInfo']:
                        definition['editorTrackingInfo']['enableEditorTracking'] = json_dict['editorTrackingInfo'][
                            'enableEditorTracking']

                    if 'enableOwnershipAccessControl' in json_dict['editorTrackingInfo']:
                        definition['editorTrackingInfo']['enableOwnershipAccessControl'] = \
                            json_dict['editorTrackingInfo']['enableOwnershipAccessControl']

                    if 'allowOthersToUpdate' in json_dict['editorTrackingInfo']:
                        definition['editorTrackingInfo']['allowOthersToUpdate'] = json_dict['editorTrackingInfo'][
                            'allowOthersToUpdate']

                    if 'allowOthersToDelete' in json_dict['editorTrackingInfo']:
                        definition['editorTrackingInfo']['allowOthersToDelete'] = json_dict['editorTrackingInfo'][
                            'allowOthersToDelete']

                    if 'allowOthersToQuery' in json_dict['editorTrackingInfo']:
                        definition['editorTrackingInfo']['allowOthersToQuery'] = json_dict['editorTrackingInfo'][
                            'allowOthersToQuery']
                    if isinstance(json_dict['editorTrackingInfo'], dict):
                        for key, val in json_dict['editorTrackingInfo'].items():
                            if key not in definition['editorTrackingInfo']:
                                definition['editorTrackingInfo'][key] = val
                if isinstance(json_dict, dict):
                    for key, val in json_dict.items():
                        if key not in definition:
                            definition[key] = val

        params = {
            "f": "json",
            "updateDefinition": json.dumps(obj=definition, separators=(',', ':')),
            "async": False
        }
        u_url = self._url + "/updateDefinition"

        res = self._con.post(u_url, params)
        self.refresh()
        return res

    # ----------------------------------------------------------------------
    def delete_from_definition(self, json_dict):
        """
        The delete_from_definition operation supports deleting a
        definition property from a hosted feature layer collection service. The result of
        this operation is a response indicating success or failure with
        error code and description.
        See http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Delete_From_Definition_Feature_Service/02r30000021w000000/ # noqa
        for additional information on this function.
        Input:
          json_dict - part to add to host service.  The part format can
                      be derived from the properties property.  For
                      layer level modifications, run updates on each
                      individual feature service layer object.  Only
                      include the items you want to remove from the
                      FeatureService or layer.

        Output:
          JSON Message as dictionary

        """
        params = {
            "f": "json",
            "deleteFromDefinition": json.dumps(json_dict),
            "async": False
        }
        u_url = self._url + "/deleteFromDefinition"

        res = self._con.post(u_url, params)
        self.refresh()
        return res


class FeatureLayerManager(_GISResource):
    """
    Allows updating the definition (if access permits) of a feature layer. This class is not created by users
    directly.
    An instance of this class, called 'manager', is available as a property of the FeatureLayer object,
    if the layer can be managed by the user.
    Users call methods on this 'manager' object to manage the feature layer.
    """

    def __init__(self, url, gis=None):
        super(FeatureLayerManager, self).__init__(url, gis)

    # ----------------------------------------------------------------------
    def refresh(self):
        """ refreshes a service """
        params = {"f": "json"}
        u_url = self._url + "/refresh"
        res = self._con.post(u_url, params)

        super(FeatureLayerManager, self)._refresh()

        return res

    # ----------------------------------------------------------------------
    def add_to_definition(self, json_dict):
        """
           The addToDefinition operation supports adding a definition
           property to a hosted feature layer. The result of this
           operation is a response indicating success or failure with error
           code and description.

           This function will allow users to change add additional values
           to an already published service.

           Input:
              json_dict - part to add to host service.  The part format can
                          be derived from the asDictionary property.  For
                          layer level modifications, run updates on each
                          individual feature service layer object.
           Output:
              JSON message as dictionary
        """

        if isinstance(json_dict, PropertyMap):
            json_dict = dict(json_dict)

        params = {
            "f": "json",
            "addToDefinition": json.dumps(json_dict),
            # "async" : False
        }
        u_url = self._url + "/addToDefinition"

        res = self._con.post(u_url, params)
        self.refresh()
        return res

    # ----------------------------------------------------------------------
    def update_definition(self, json_dict):
        """
           The updateDefinition operation supports updating a definition
           property in a hosted feature layer. The result of this
           operation is a response indicating success or failure with error
           code and description.

           Input:
              json_dict - part to add to host service.  The part format can
                          be derived from the asDictionary property.  For
                          layer level modifications, run updates on each
                          individual feature service layer object.
           Output:
              JSON Message as dictionary
        """

        if isinstance(json_dict, PropertyMap):
            json_dict = dict(json_dict)

        params = {
            "f": "json",
            "updateDefinition": json.dumps(json_dict),
            "async": False
        }

        u_url = self._url + "/updateDefinition"

        res = self._con.post(u_url, params)
        self.refresh()
        return res

    # ----------------------------------------------------------------------
    def delete_from_definition(self, json_dict):
        """
           The deleteFromDefinition operation supports deleting a
           definition property from a hosted feature layer. The result of
           this operation is a response indicating success or failure with
           error code and description.
           See: http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Delete_From_Definition_Feature_Service/02r30000021w000000/ # noqa
           for additional information on this function.
           Input:
              json_dict - part to add to host service.  The part format can
                          be derived from the asDictionary property.  For
                          layer level modifications, run updates on each
                          individual feature service layer object.  Only
                          include the items you want to remove from the
                          FeatureService or layer.

           Output:
              JSON Message as dictionary

        """

        if isinstance(json_dict, PropertyMap):
            json_dict = dict(json_dict)

        params = {
            "f": "json",
            "deleteFromDefinition": json.dumps(json_dict)
        }
        u_url = self._url + "/deleteFromDefinition"

        res = self._con.post(u_url, params)
        self.refresh()
        return res
