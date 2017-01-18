"""
"""
import os
from .._common._base import BaseServer
########################################################################
class FeatureService(BaseServer):
    """
    A feature service can contain datasets (for example, tables and views)
    with or without a spatial column. Datasets with a spatial column are
    considered layers; those without a spatial column are considered
    tables. A feature service allows clients to query and edit feature
    geometry and attributes.
    This resource provides basic information about the feature service,
    including the feature layers and tables that it contains, the service
    description, and so on.
    The capabilities property returns Create, Delete, Extract, Query,
    Update, Sync, and Uploads capabilities. The Uploads capability is
    included if Create, Delete, or Update is enabled for a feature service.
    The Editing capability is included if Create, Delete, and Update is
    enabled and allowGeometryUpdates is true. The Sync capability allows
    editors to make local edits and periodically sync with the feature
    service. The Extract capability allows editors to create a local copy
    of data without the ability to sync with the feature service.
    The maxRecordCount property returns the maximum number of records that
    will be returned at once for a query. The Feature Service resource has
    an input parameters option and outSR to support viewing of a feature
    service footprint in arcgis.com.
    """
    _url = None
    _con = None
    _tables = None
    _layers = None
    #----------------------------------------------------------------------
    @property
    def layers(self):
        """gets the layers related to a feature service"""
        lyrs = []
        if self._layers is None:
            self.init()
        for layer in self._layers:
            if "id" in layer:
                layer_id = layer['id']
                url = "{url}/{id}".format(url=self._url, id=layer_id)
                layer_type = self._get_layer_type(layer_id=layer['id'])
                if layer_type == "Feature Layer":
                    lyrs.append(FeatureLayer(url=url,connection=self._con))
                elif layer_type == "Raster Layer":
                    lyrs.append(RasterLayer(url=url,connection=self._con))
                elif layer_type == "Group Layer":
                    lyrs.append(GroupLayer(url=url,connection=self._con))
            del layer
        return lyrs
    #----------------------------------------------------------------------
    @property
    def tables(self):
        """gets the tables related to a feature service"""
        lyrs = []
        if self._tables is None:
            self.init()
        for layer in self._tables:
            url = "{url}/{id}".format(url=self._url, id=layer['id'])
            layer_type = self._get_layer_type(layer_id=layer['id'])
            if layer_type == "Table Layer":
                lyrs.append(TableLayer(url=url, connection=self._con))
            elif layer_type == "Group Layer":
                lyrs.append(GroupLayer(url=url, connection=self._con))
        return lyrs
    #----------------------------------------------------------------------
    def _get_layer_type(self, layer_id):
        url = "{url}/{id}".format(url=self._url, id=layer_id)
        params = {"f": "json"}
        res = self._con.get(path=url, params=params)
        return res['type']
    #----------------------------------------------------------------------
    @property
    def administration(self):
        """accesses the administration service"""
        url = self._url
        res = search("/rest/", url).span()
        addText = "admin/"
        part1 = url[:res[1]]
        part2 = url[res[1]:]
        adminURL = "%s%s%s" % (part1, addText, part2)

        res = AdminFeatureService(url=adminURL,
                                  connection=self._con,
                                  initialize=True)
        return res
    #----------------------------------------------------------------------
    def refresh(self):
        """reloads all the services properties"""
        self.init(connection=self._con)
    #----------------------------------------------------------------------
    def apply_edits(self,
                    edits,
                    gdbVersion=None,
                    honorSequenceOfEdits=False,
                    returnEditMoment=False,
                    rollbackOnFailure=True,
                    useGlobalIds=False,
                    trueCurveClient=False
                    ):
        """
        The applyEdits operation applies edits to features associated with
        multiple layers or tables in a single call (POST only). This
        operation is performed on a feature service resource. The result of
        this operation is an array of edit results for each layer/table
        edited. Each edit result identifies a single feature on a layer or
        table and indicates whether the edits were successful or not. If an
        edit is not successful, the edit result also includes an error code
        and an error description.

        Parameters:
         :edits:The array of layers and edits to be applied. Features to be
          added or updated to a feature layer should include the geometry.
          Records to be added or updated to a table should not include the
          geometry. If useGlobalIds is true, the features are added while
          preserving their globalIds. For new features and attachments, the
          client must generate globalIds. In order for a feature or
          attachment to be updated or deleted, clients must include its
          globalId. If useGlobalIds is false (default), globalIds submitted
          with the features are ignored and new globalids are assigned when
          features are added. In order for a feature to be updated or
          deleted, the attributes property of the feature must include the
          object ID of the feature along with the other attributes.
          Attachments are not supported as an edit payload when
          useGlobalIds is false.
          *Syntax Example*
          [
            { "id" : <layerId1>,
                "adds" : [<feature1>, <feature2>],
                "updates" : [<feature1>, <feature2>],
                "deletes" : [<objectID1>, <objectID2>]
            },
            { "id" : <layerId2>,
                "adds" : [<feature1>, <feature2>],
                "updates" : [<feature1>, <feature2>],
                "deletes" : [<objectID1>, <objectID2>]
            }
          ]
         :gdbVersion:Geodatabase version to apply the edits. This parameter
          applies only if the isDataVersioned property of the layer is true
         :honorSequenceOfEdits: This option was added at 10.5 and works
          with ArcGIS Server services only. Optional parameter specifying
          whether to apply edits in the order they are submitted in the
          JSON. If honorSequenceOfEdits = true, edits will apply in the
          submitted order. If honorSequenceOfEdits = false, which is the
          default, edits will apply in ascending layer-ID order. All the
          edits for the layer with the lowest ID will apply first.
         :returnEditMoment: Optional parameter specifying whether the
          response will report the time edits were applied. If
          returnEditMoment = true, the server will return the time edits
          were applied in the response's editMoment key.
         :rollbackOnFailure:Optional parameter to specify if the edits
          should be applied only if all submitted edits succeed. If false,
          the server will apply the edits that succeed even if some of the
          submitted edits fail. If true, the server will apply the edits
          only if all edits succeed. The default value is true.
         :useGlobalIds:Optional parameter which is false by default.
          Requires the service's supportsApplyEditsWithGlobalIds property
          to be true.
         :trueCurveClient:  Optional parameter which is false by default is
          set by client to indicate to the server that client in true curve
          capable.
        """
        url = "{url}/applyEdits".format(url=self._url)
        params = {
            "f" : "json",
            "edits" : edits
        }
        if gdbVersion:
            params['gdbVersion'] = gdbVersion
        if honorSequenceOfEdits:
            params['honorSequenceOfEdits'] = honorSequenceOfEdits
        if returnEditMoment:
            params['returnEditMoment'] = returnEditMoment
        if rollbackOnFailure:
            params['rollbackOnFailure'] = rollbackOnFailure
        if useGlobalIds:
            params['useGlobalIds'] = useGlobalIds
        if trueCurveClient:
            params['trueCurveClient'] = trueCurveClient
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def create_replica(self,
                       layers,
                       layerQueries,
                       geometry,
                       geometryType,
                       transportType,
                       syncModel,
                       replicaName=None,
                       dataFormat="json",
                       inSR=None,
                       repliceSR=None,
                       targetType='client',
                       returnAttachments=False,
                       returnAttachmentsDatabyURL=False,
                       attachmentsSyncDirection="none",
                       async=False,
                       replicaOptions=None
                       ):
        """
        The createReplica operation is performed on a feature service
        resource. This operation creates the replica between the feature
        service and a client based on a client-supplied replica definition.
        It requires the Sync capability. See Sync overview for more
        information on sync.bThe response for createReplica includes
        replicaID, server generation number, and data similar to the
        response from the feature service query operation.
        The createReplica operation returns a response of type
        esriReplicaResponseTypeData, as the response has data for the layers
        in the replica. If the operation is called to register existing data
        by using replicaOptions, the response type will be
        esriReplicaResponseTypeInfo, and the response will not contain data
        for the layers in the replica.

        Parameters:
         :replicaName:The name of the replica on the server. The replica
          name is unique per feature service. This is not a required
          parameter. If not specified, a replica name will be assigned and
          returned in the createReplica response. If specified, but the
          replicaName already exists on the server, a unique name will be
          returned in the response using the given replicaName as a base
          (that is, MyReplica may be returned as MyReplica_0 if there is
          already a replica named MyReplica on the server).
         :layers: The list of layers and tables to include in the replica.
         :layerQueries: In addition to the layers and geometry parameters,
          the layerQueries parameter can be used to further define what is
          replicated. This parameter allows you to set properties on a
          per-layer or per-table basis. Only the properties for the layers
          and tables that you want changed from the default are required.
         :geometry: The geometry to apply as the spatial filter. All the
          features in layers intersecting this geometry will be replicated.
          The structure of the geometry is the same as the structure of the
          JSON geometry objects returned by the ArcGIS REST API. In
          addition to the JSON structures, for envelopes and points, you
          can specify the geometry with a simpler comma-separated syntax.
         :geometryType: The type of geometry specified by the geometry
          parameter. The geometry type can be an envelope, point, line, or
          polygon. The default geometry type is an envelope.
          Values: esriGeometryPoint | esriGeometryMultipoint |
          esriGeometryPolyline | esriGeometryPolygon | esriGeometryEnvelope
         :transportType:Specifies whether the replica is to be used on a
          client, such as a mobile device or ArcGIS Pro, or on another
          server. Specifying server allows you to publish the replica to
          another portal and then synchronize changes between two feature
          services. The default is client. Values: client | server
         :syncModel: This parameter is used to indicate that the replica is
          being created for per-layer sync or per-replica sync. To
          determine which model types are supported by a service, query the
          supportsPerReplicaSync, supportsPerLayerSync, and
          supportsSyncModelNone properties of the Feature Service. By
          default, a replica is created for per-replica sync. If syncModel
          is perReplica, the syncDirection specified during sync applies to
          all layers in the replica. If the syncModel is perLayer, the
          syncDirection is defined on a layer-by-layer basis.
          If syncModel is perReplica, the response will have
          replicaServerGen. A perReplica syncModel requires the
          replicaServerGen on sync. The replicaServerGen tells the server
          the point in time from which to send back changes.
          If syncModel is perLayer, the response will include an array of
          server generation numbers for the layers in layerServerGens. A
          perLayer sync model requires the layerServerGens on sync. The
          layerServerGens tell the server the point in time from which to
          send back changes for a specific layer.
          syncModel=none can be used to export the data without creating a
          replica. Query the supportsSyncModelNone property of the feature
          service to see if this model type is supported.
          See the RollbackOnFailure and Sync Models topic for more details.
          Values: perReplica | perLayer | none
         :dataFormat: The format of the replica geodatabase returned in the
          response. The default is json.
          Syntax: sqlite | json
         :inSR: The spatial reference of the input geometry.
         :repliceSR: The spatial reference of the replica geometry.
         :targetType:The transportType represents the response format. If
          the transportType is esriTransportTypeUrl, the JSON response is
          contained in a file, and the URL link to the file is returned.
          Otherwise, the JSON object is returned directly. The default is
          esriTransportTypeUrl.
          If async is true, the results will always be returned as if
          transportType is esriTransportTypeUrl. If dataFormat is sqlite,
          the transportFormat will always be esriTransportTypeUrl
          regardless of how the parameter is set.
          Values: esriTransportTypeUrl | esriTransportTypeEmbedded
         :returnAttachments:If true, attachments are added to the replica
          and returned in the response. Otherwise, attachments are not
          included. The default is false. This parameter is only applicable
          if the feature service has attachments.
          Values: true | false
         :returnAttachmentsDatabyURL: If true, a reference to a URL will be
          provided for each attachment returned from createReplica.
          Otherwise, attachments are embedded in the response. The default
          is true. This parameter is only applicable if the feature service
          has attachments and if returnAttachments is true and f=json.
          Values: true | false
         :attachmentsSyncDirection: Clients can specify the
          attachmentsSyncDirection when creating a replica. This parameter
          defines how attachments will be synced and is only applicable if
          the feature service has attachments.
           Values include:
            bidirectional - Attachment edits can be both uploaded from the
             client and downloaded from the service when syncing.
            Upload - Attachment edits can only be uploaded from the client
             when syncing. When the client calls synchronizeReplica,
             feature and row edits will be downloaded but attachments will
             not be. This is useful in cases where the data collector does
             not want to consume space with attachments from the service,
             but does need to collect new attachments.
            None - Attachment edits are never synced from either the client
             or the server.
          When returnAttachments is set to true, you can set
          attachmentsSyncDirection to either bidirectional (default) or
          upload. In this case, create replica includes attachments from
          the service.
          When returnAttachments is set to false, you can set
          attachmentsSyncDirection to either upload or none (default). In
          this case, create replica does not include attachments from the
          service.
          All other combinations are not valid.
          AttachmentsSyncDirection is set during the createReplica
          operation and cannot be overridden during sync.
          Values: bidirectional | upload | none
         :async: If true, the request is processed as an asynchronous job,
          and a URL is returned that a client can visit to check the status
          of the job. See the topic on asynchronous usage for more
          information. The default is false.
         :replicaOptions: This parameter instructs the createReplica
          operation to create a new replica based on an existing replica
          definition (refReplicaId). It can be used to specify parameters
          for registration of existing data for sync. The operation will
          create a replica but will not return data. The responseType
          returned in the createReplica response will be
          esriReplicaResponseTypeInfo.
        """
        url = "{url}/createReplica".format(url=self._url)
        params = {
            "f" : "json",
            "layers" : layers,
            "geometry" : geometry,
            "geometryType":geometryType,
            "transportType" : transportType,
            "syncModel" : syncModel,
            "returnAttachmentsDatabyURL" : returnAttachmentsDatabyURL,
            "returnAttachments" : returnAttachments,
            'async' : async
        }
        if layerQueries:
            params['layerQueries'] = layerQueries
        if replicaName:
            params['replicaName'] = replicaName
        if dataFormat:
            params['dataFormat'] = dataFormat
        if inSR:
            params['inSR'] = inSR
        if repliceSR:
            params['replicaSR'] = repliceSR
        if targetType:
            params['targetType'] = targetType
        if attachmentsSyncDirection:
            params['attachmentsSyncDirection'] = attachmentsSyncDirection
        if replicaOptions:
            params['replicaOptions'] = replicaOptions
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def query(self,
              layerDefs,
              geometry=None,
              geometryType="envelope",
              inSR=None,
              spatialRel="esriSpatialRelIntersects",
              time=None,
              outSR=None,
              historicMoment=None,
              returnGeometry=True,
              maxAllowableOffset=None,
              returnIdsOnly=False,
              returnCountOnly=False,
              returnZ=False,
              returnM=False,
              geometryPrecision=None,
              returnTrueCurves=False,
              sqlFormat="none",
              gdbVersion=None
              ):
        """
        The Query operation is performed on a feature service resource. The
        result of this operation is either a feature set for each layer in
        the query or a count of features for each layer (if returnCountOnly
        is set to true) or an array of feature IDs for each layer in the
        query (if returnIdsOnly is set to true).
        While there is a limit to the number of features included in the
        response (see the maxRecordCount property of the feature service),
        there is no limit to the number of object IDs returned in the ID
        array response. Clients can exploit this to get all the query
        conforming object IDs by specifying returnIdsOnly=true and
        subsequently requesting feature sets for subsets of object IDs.
        In the feature set response, the layer features include their
        geometries. The records for tables do not.

        Parameters:
         :layerDefs:  Allows you to filter the features of individual
          layers in the query by specifying definition expressions for
          those layers. A definition expression for a layer that is
          published with the service will always be honored.
         :geometry: The geometry to apply as the spatial filter. The
          structure of the geometry is the same as the structure of the
          json geometry objects returned by the ArcGIS REST API. In
          addition to the JSON structures, for envelopes and points, you
          can specify the geometry with a simpler comma-separated syntax.
         :geometryType:The type of geometry specified by the geometry
          parameter. The geometry type can be an envelope, point, line, or
          polygon. The default geometry type is an envelope.
          Values: esriGeometryPoint | esriGeometryMultipoint |
          esriGeometryPolyline | esriGeometryPolygon | esriGeometryEnvelope
         :inSR: The spatial reference of the input geometry.
         :spatialRel:The spatial relationship to be applied on the input
          geometry while performing the query. The supported spatial
          relationships include intersects, contains, envelope intersects,
          within, and so on. The default spatial relationship is intersects
          (esriSpatialRelIntersects).
          Values: esriSpatialRelIntersects | esriSpatialRelContains |
          esriSpatialRelCrosses | esriSpatialRelEnvelopeIntersects |
          esriSpatialRelIndexIntersects | esriSpatialRelOverlaps |
          esriSpatialRelTouches | esriSpatialRelWithin
         :time:The time instant or the time extent to query.
         :outSR: The spatial reference of the returned geometry.
         :gdbVersion:The geodatabase version to query. This parameter
          applies only if the hasVersionedData property of the service and
          the isDataVersioned property of the layer(s) queried are true.
         :historicMoment:The historic moment to query. This parameter
          applies only if the supportsQueryWithHistoricMoment property of
          the layers being queried is set to true. This setting is provided
          in the layer resource.
         :returnGeometry:If true, the result includes the geometry
          associated with each feature returned. The default is true
         :maxAllowableOffset:This option can be used to specify the
          maxAllowableOffset to be used for generalizing geometries
          returned by the query operation.
         :returnIdsOnly:If true, the response only includes an array of
          object IDs for each layer. Otherwise, the response is a feature
          set. The default is false.
          While there is a limit to the number of features included in the
          feature set response, there is no limit to the number of object
          IDs returned in the ID array response. Clients can exploit this
          to get all the query conforming object IDs by specifying
          returnIdsOnly=true and subsequently requesting feature sets for
          subsets of object IDs.
         :returnCountOnly:If true, the response only includes the count
          (number of features/records) that would be returned by a query.
          Otherwise, the response is a feature set. The default is false.
         :returnZ:If true, Z values are included in the results if the
          features have Z values. Otherwise, Z values are not returned. The
          default is false.
         :returnM: If true, M values are included in the results if the
          features have M values. Otherwise, M values are not returned. The
          default is false.
         :geometryPrecision:This option can be used to specify the number
          of decimal places in the response geometries returned by the
          query operation.
         :returnTrueCurves:Optional parameter which is false by default.
         :sqlFormat:The sqlFormat parameter can be either standard SQL92
          standard or it can use the native SQL of the underlying datastore
          native. The default is none which means the sqlFormat depends on
          useStandardizedQuery parameter.
          Values: none | standard | native
        """
        params = {"f" : "json",
                  "layerDefs" : layerDefs}
        url = "{url}/query".format(url=self._url)
        if maxAllowableOffset:
            params['maxAllowableOffset'] = maxAllowableOffset
        if geometry:
            params['geometry'] = geometry
        if geometryType:
            params['geometryType'] = geometryType
        if inSR:
            params['inSR'] = inSR
        if spatialRel:
            params['spatialRel'] = spatialRel
        if time:
            params['time'] = time
        if outSR:
            params['outSR'] = outSR
        if gdbVersion:
            params['gdbVersion'] = gdbVersion
        if historicMoment:
            params['historicMoment'] = historicMoment

        params['returnGeometry'] = returnGeometry
        params['returnIdsOnly'] = returnIdsOnly
        params['returnCountyOnly'] = returnCountOnly
        params['returnZ'] = returnZ
        params['returnM'] = returnM
        if geometryPrecision:
            params['geometryPrecision'] = geometryPrecision
        params['returnTrueCurves'] = returnTrueCurves
        if sqlFormat:
            params['sqlFormat'] = sqlFormat
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def query_domains(self, layers):
        """
        This operation was added at 10.5. Services that support the
        queryDomains operation include the supportsQueryDomains property
        set to true in the service resource.
        The queryDomains operation returns full domain information for the
        domains referenced by the layers in the service. This operation is
        performed on a feature service resource. The operation takes an
        array of layer IDs and returns the set of domains referenced by the
        layers.
        This operation can be used by clients to efficiently work with
        domains. For example, a client can use the queryDomains operation
        to get and cache domain information once. When getting layer
        information from the layer resource, clients can then use the
        returnDomainNames=true parameter to get just the domain names in
        the layer resource. The domain names can then be used to find the
        full domain information in the cache.

        Parameters:
         :layers: An array of layers.
        """
        url = "{url}/queryDomains".format(url=self._url)
        params = {"f" : "json"}
        return self._con.get(path=url, params=params)
    #----------------------------------------------------------------------
    @property
    def replicas(self):
        """
        The replicas resource lists all replicas that have been created on
        the feature service. This list includes the replica name and
        replica ID of each replica. For secured services, all replicas are
        listed when logged in as the admin user. Otherwise, only replicas
        created by the logged-in user are listed.
        """
        url = "{url}/replicas".format(url=self._url)
        params = {"f" : "json"}
        return self._con.get(path=url, params=params)
    #----------------------------------------------------------------------
    @property
    def replica_info(self, replicaId):
        """
        The replica info resources lists replica metadata for a specific
        replica.

        Parameters:
         :replicaId: unique id of the replica to get information about.
        """
        url = "{url}/replicas/{uid}".format(url=self._url,
                                            uid=replicaId)
        params = {"f" : "json"}
        return self._con.get(path=url, params=params)
    #----------------------------------------------------------------------
    def synchronize_replica(self,
                            replicaID,
                            transportType,
                            dataFormat,
                            replicaServerGen=None,
                            closeReplica=False,
                            returnIdsForAdds=False,
                            edits=None,
                            returnAttachmentDatabyURL=True,
                            async=False,
                            syncDirection=None,
                            syncLayers=None,
                            editsUploadID=None,
                            editsUploadFormat=None,
                            rollbackOnFailure=True
                            ):
        """
        The synchronizeReplica operation is performed on a feature service
        resource. This operation synchronizes changes between the feature
        service and a client based on the replicaID provided by the client.
        Requires the sync capability. See Sync overview for more
        information on sync.
        The client obtains the replicaID by first calling the createReplica
        operation.
        Synchronize applies the client's data changes by importing them
        into the server's geodatabase. It then exports the changes from the
        server geodatabase that have taken place since the last time the
        client got the data from the server. Edits can be supplied in the
        edits parameter, or, alternatively, by using the editsUploadId and
        editUploadFormat to identify a file containing the edits that were
        previously uploaded using the upload_item operation.
        The response for this operation includes the replicaID, new replica
        generation number, or the layer's generation numbers. The response
        has edits or layers according to the syncDirection/syncLayers.
        Presence of layers and edits in the response is indicated by the
        responseType.
        If the responseType is esriReplicaResponseTypeEdits or
        esriReplicaResponseTypeEditsAndData, the result of this operation
        can include arrays of edit results for each layer/table edited as
        specified in edits. Each edit result identifies a single feature on
        a layer or table and indicates if the edits were successful or not.
        If an edit is not successful, the edit result also includes an
        error code and an error description.
        If syncModel is perReplica and syncDirection is download or
        bidirectional, the synchronizeReplica operation's response will
        have edits. If syncDirection is snapshot, the response will have
        replacement data.
        If syncModel is perLayer, and syncLayers have syncDirection as
        download or bidirectional, the response will have edits. If
        syncLayers have syncDirection as download or bidirectional for some
        layers and snapshot for some other layers, the response will have
        edits and data. If syncDirection for all the layers is snapshot,
        the response will have replacement data.
        When syncModel is perReplica, the createReplica and
        synchronizeReplica operations' responses contain replicaServerGen.
        When syncModel is perLayer, the createReplica and
        synchronizeReplica operations' responses contain layerServerGens.

        Parameters:
         :replicaID:The ID of the replica you want to synchronize.
         :transportType:transportType represents the response format. If
          the transportType is esriTransportTypeUrl, the operation's
          response is contained in a file, and the URL link to the file is
          returned. Otherwise, the JSON object is returned directly in the
          response. The default is esriTransportTypeUrl. Note that for
          asynchronous processing (async=true), or when the response is
          returned in sqlite (dataFormat=sqlite ), results are always
          returned via URL regardless of how the parameter is set.
          Values: esriTransportTypeUrl | esriTransportTypeEmbedded
         :dataFormat:The data format for the returned data.
          Values: json | sqlite
         :replicaServerGen:replicaServerGen is a generation number that
          allows the server to keep track of what changes have already been
          synchronized. A new replicaServerGen is sent with the response to
          the synchronizeReplica operation. Clients should persist this
          value and use it with the next synchronizeReplica call.
          It applies to replicas with syncModel = perReplica.
          For replicas with syncModel = perLayer, layer generation numbers
          are specified using parameter: syncLayers; and replicaServerGen
          is not needed.
         :closeReplica:If true, the replica will be unregistered when the
          synchronize completes. This is the same as calling synchronize
          and then calling unregisterReplica. Otherwise, the replica can
          continue to be synchronized. The default is false.
         :returnIdsForAdds:If true, the objectIDs and globalIDs of features
          added during the synchronize will be returned to the client in
          the addResults sections of the response. Otherwise, the IDs are
          not returned. The default is false.
         :edits:The edits the client wants to apply to the service.
         Alternatively, the editsUploadID and editsUploadFormat can be
         used to specify the edits in a delta file.
         The edits are described using an array where an element in the
         array includes:
          - The layer or table ID
          - The feature or row edits to apply listed as inserts, updates,
            and deletes
          - The attachments to apply listed as inserts, updates, and
            deletes
         For features, adds and updates are specified as feature objects
         that include geometry and attributes.
         Deletes can be specified using globalIDs for features and
         attachments.
         For attachments, updates and adds are specified using the
         following set of properties for each attachment. If embedding the
         attachment, set the data property; otherwise, set the url
         property. All other properties are required:
          - globalid-The globalID of the attachment that is to be added or
            updated.
          - parentGlobalid-The globalID of the feature associated with the
            attachment.
          - contentType-Describes the file type of the attachment (for
            example, image/jpeg).
          - name-The file name (for example, hydrant.jpg).
          - data-The base 64 encoded data if embedding the data. Only
            required if the attachment is embedded.
          - url-The location where the service will upload the attachment
            file (for example,
            http://machinename/arcgisuploads/Hydrant.jpg). Only required if
            the attachment is not embedded.
         Syntax:
          [
            {
            "id" : <layerId1>,
            "features" : {
                    "adds" : [<feature1>, <feature2>],
                    "updates" : [<feature1>, <feature2>],
                    "deleteIds" : [<globalID1>, <globalID2>]},
            "attachments" : {
                    "adds" : [ <attachment1>, <attachment2> ],
                    "updates" : [ <attachment1>, <attachment2> ],
                    "deleteIds" : [ <attachment1>, <attachment2> ]},
            },
            {
            "id" : <layerId2>,
            "features" : {
                    "adds" : [<feature1>, <feature2>],
                    "updates" : [<feature1>, <feature2>],
                    "deleteIds" : [<globalID1>, <globalID2>]},
            "attachments" : {
                    "adds" : [<attachment1>, <attachment2> ],
                    "updates" : [<attachment1>, <attachment2> ],
                    "deleteIds" : [ <globalID1>, <globalID2> ]},
            }
          ]
         :returnAttachmentDatabyURL:If true, a reference to a URL will be
          provided for each attachment returned from synchronizeReplica.
          Otherwise, attachments are embedded in the response. The default
          is true.
          Applies only if attachments are included in the replica.
         :async:If true, the request is processed as an asynchronous job
          and a URL is returned that a client can visit to check the status
          of the job. See the topic on asynchronous usage for more
          information. The default is false.
         :syncDirection:Determines whether to upload, download, or upload
          and download on sync. By default, a replica is synchronized
          bi-directionally. Only applicable when syncModel = perReplica.
          If syncModel = perLayer, sync direction is specified using
          syncLayers.
          Values: download | upload | bidirectional | snapshot
         :syncLayers:syncLayers allows a client to specify layer-level
          generation numbers for a sync operation. It can also be used to
          specify sync directions at layer-level. This parameter is needed
          for replicas with syncModel = perLayer. It is ignored for
          replicas with syncModel = perReplica.
          serverGen is required for layers with syncDirection =
          bidirectional or download.
          If a sync operation has both the syncDirection and
          syncLayersparameters, and the replica's syncModel is perLayer,
          the layers that do not have syncDirection values will use the
          value of the syncDirection parameter. If the syncDirection
          parameter is not specified, the default value of bidirectional is
          used.
          Values: download | upload | bidirectional | snapshot
         :editsUploadID:The ID for the uploaded item that contains the
          edits the client wants to apply to the service. Used in
          conjunction with editsUploadFormat.
         :editsUploadFormat: The data format of the uploaded data reference
          in editsUploadId.
          Values: sqlite
         :rollbackOnFailure:Determines the behavior when there are errors
          while importing edits on the server during synchronization. This
          only applies in cases where edits are being uploaded to the
          server (syncDirection = upload or bidirectional). See the
          RollbackOnFailure and Sync Models topic for more details.
          When true, if an error occurs while importing edits on the server
          all edits are rolled back (not applied), and the operation
          returns an error in the response. Use this setting when the edits
          are such that you will either want all or none applied.
          When false, if an error occurs while importing an edit on the
          server, the import process skips the edit and continues. All
          edits that were skipped are returned in the edits results with
          information describing why the edits were skipped.
        """
        params = {
            "f" : "json",
            "replicaID" : replicaID,
            "transportType" : transportType,
            "dataFormat" : dataFormat,
            "async" : async,
            "returnAttachmentDatabyURL" : returnAttachmentDatabyURL,
            "rollbackOnFailure" : rollbackOnFailure
        }
        url = "{url}/synchronizeReplica".format(url=self._url)
        if replicaServerGen:
            params['replicaServerGen'] = replicaServerGen
        if closeReplica:
            params['closeReplica'] = closeReplica
        if returnIdsForAdds:
            params['returnIdsForAdds'] = returnIdsForAdds
        if edits:
            params['edits'] = edits
        if syncDirection:
            params['syncDirection'] = syncDirection
        if syncLayers:
            params['syncLayers'] = syncLayers
        if editsUploadID:
            params['editsUploadID'] = editsUploadID
        if editsUploadFormat:
            params['editsUploadFormat'] = editsUploadFormat
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def unregister_replica(self, replicaID):
        """
        The unRegisterReplica operation is performed on a feature service
        resource. This operation unregisters a replica on the feature
        service. It requires the Sync capability. See Sync overview for
        more information on sync.

        Parameters:
         :replicaID: The replicaID returned by the feature service when the
          replica was created.
        """
        params = {
            "f" : "json",
            "replicaID" : replicaID
        }
        url = "{url}/unRegisterReplica".format(url=self._url)
        return self._con.post(path=url,
                              postdata=params)


########################################################################
class FeatureLayer(BaseServer):
    """
    The layer resource represents a single feature layer or a non-spatial
    table in a feature service. A feature layer is a table or view with at
    least one spatial column.
    For tables, it provides basic information about the table such as its
    ID, name, fields, types, and templates. For feature layers, in addition
    to the table information, it provides information such as its geometry
    type, min and max scales, and spatial reference. Each type includes
    information about the type, such as the type ID, name, and definition
    expression. Types also include a default symbol and a list of feature
    templates. Each feature template includes a template name, description,
    and prototypical feature.
    The property capabilities return Query, Create, Delete, Update,
    Editing, Sync, Uploads and Extract capabilities. The Editing capability
    will be included if Create, Delete, or Update is enabled for a feature
    service.
    The maxRecordCount property returns the maximum number of records that
    will be returned at once for a query.
    The Layer resource returns relatedTableId, cardinality, role, keyField,
    and composite for all relationships. In addition, the
    relationshiptableId and keyFieldInRelationshipTable properties are
    returned for attributed relationships only.
    The effectiveMinScale and effectiveMaxScale properties represent the
    effective minimum and maximum scales at which the layer is visible.
    Effective minimum and maximum scale are calculated based on the minScale
    and maxScale values of the current layer and its ancestors.
    The Layer resource supports an input parameter returnUpdates that
    accepts a Boolean value. Pass this parameter to retrieve updated
    timeExtent for the layer.
    The field property nullable indicates whether the field can accept null
    values.
    If a layer has attachments, its hasAttachments property will be true.
    If the layer objectIdField does not have a length property or the length
    property is set to 4, the objectIdField is 32-bit. If the objectIdField
    has a length of 8, the objectIdField is 64-bit.
    """
    _con = None
    _url = None
    #----------------------------------------------------------------------
    @property
    def administration(self):
        """accesses the administration service"""
        url = self._url
        res = search("/rest/", url).span()
        addText = "admin/"
        part1 = url[:res[1]]
        part2 = url[res[1]:]
        adminURL = "%s%s%s" % (part1, addText, part2)

        res = AdminFeatureServiceLayer(url=adminURL,
                                       connection=self._con,
                                       initialize=True)
        return res
    #----------------------------------------------------------------------
    def refresh(self):
        """refreshes all the properties of the service"""
        self._json_dict = None
        self.init(self._con)
    #----------------------------------------------------------------------
    def add_attachment(self,
                       oid,
                       filePath=None,
                       returnEditMoment=False,
                       uploadId=None,
                       gdbVersion=None):
        """
        """
        url = "{url}/{oid}/addAttachment".format(url=self._url,
                                                 oid=oid)
        params = {
            "f" : "json",
        }
        if filePath and \
           os.path.isfile(filePath):
            files = {
                "attachment" : filePath
            }
        else:
            files = {}
        if uploadId:
            params['uploadId'] = uploadId
        if returnEditMoment:
            params['returnEditMoment'] = returnEditMoment
        if gdbVersion:
            params['gdbVersion'] = gdbVersion
        return self._con.post(url=url,
                              postdata=params,
                              files=files)

    #----------------------------------------------------------------------
    def add_features(self,
                     features,
                     gdbVersion=None,
                     returnEditMoment=False,
                     rollbackOnFailure=True
                     ):
        """
        This operation adds features to the associated feature layer or
        table (POST only). The addFeatures operation is performed on a
        feature service layer resource.
        The operation returns the results of the edits in an array of edit
        result objects. Each edit result identifies a single feature and
        indicates if the inserts were successful or not. If not, it also
        includes an error code and an error description.

        Parameters:
         :features: The array of features to be added. The structure of
          each feature in the array is the same as the structure of the
          json feature object returned by the ArcGIS REST API.
          Example:
           [
            {
              "geometry" : {"x" : -118.15, "y" : 33.80},
              "attributes" : {
                "OWNER" : "Joe Smith",
                "VALUE" : 94820.37,
                "APPROVED" : true,
                "LASTUPDATE" : 1227663551096
              }
            },
            {
              "geometry" : { "x" : -118.37, "y" : 34.086 },
              "attributes" : {
                "OWNER" : "John Doe",
                "VALUE" : 17325.90,
                "APPROVED" : false,
                "LASTUPDATE" : 1227628579430
              }
            }
          ]
         :gdbVersion: Geodatabase version to apply the edits. This parameter
          applies only if the isDataVersioned property of the layer is true.
          If the gdbVersion parameter is not specified, edits are made to
          the published map's version.
          Features to be added to a feature layer should include the
          geometry. Records to be added to a table should not include the
          geometry.
         :returnEditMoment: Optional parameter specifying whether the
          response will report the time features were added. If
          returnEditMoment = true, the server will report the time in the
          response's editMoment key. The default value is false.
         :rollbackOnFailure: Optional parameter to specify if the edits
          should be applied only if all submitted edits succeed. If false,
          the server will apply the edits that succeed even if some of the
          submitted edits fail. If true, the server will apply the edits
          only if all edits succeed. The default value is true.
        """
        url = "{url}/addFeatures".format(url=self._url)
        params = {
            "f" : "json",
            "features" : features
        }
        if gdbVersion:
            params['gdbVersion'] = gdbVersion
        if returnEditMoment:
            params['returnEditMoment'] = returnEditMoment
        if rollbackOnFailure:
            params['rollbackOnFailure'] = rollbackOnFailure
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def apply_edits(self,
                    adds=None,
                    updates=None,
                    deletes=None,
                    gdbVersion=None,
                    returnEditMoment=False,
                    rollbackOnFailure=True,
                    useGlobalIds=False,
                    attachments=None,
                    trueCurveClient=False
                    ):
        """
         :adds: The array of features to be added. The structure of each
          feature in the array is the same as the structure of the json
          feature object returned by the ArcGIS REST API.
          Features to be added to a feature layer should include the
          geometry. Records to be added to a table should not include
          geometry. If useGlobalIds is true, the features are added while
          preserving their globalIds. If useGlobalIds is false or not
          specified, the globalIds submitted with the features are ignored
          and the service assigns new globalIds to the new features.
         :updates: The array of features to be updated. The structure of
          each feature in the array is the same as the structure of the
          json feature object returned by the ArcGIS REST API and includes
          a globalId.
         :deletes:The object IDs of the features/records to be deleted.
         :attachments: Optional parameter which requires the layer's
          supportsApplyEditsWithGlobalIds property to be true. Use the
          attachments parameter to add, update or delete attachments.
          Applies only when the useGlobalIds parameter is set to true. For
          adds, the globalIds of the attachments provided by the client are
          preserved. When useGlobalIds is true, updates and deletes are
          identified by each feature or attachment globalId rather than
          their objectId or attachmentId.
          *Attachment Syntax*
          {
            "adds": [<attachment1>, <attachment2>],
            "updates": [<attachment1>, <attachment2>],
            "deletes": ["<attachmentGlobalId1>", "<attachmentGlobalId2>"]
          }
         :gdbVersion:Geodatabase version to apply the edits. This parameter
          applies only if the isDataVersioned property of the layer is true
         :returnEditMoment: Optional parameter specifying whether the
          response will report the time edits were applied. If
          returnEditMoment = true, the server will return the time edits
          were applied in the response's editMoment key.
         :rollbackOnFailure:Optional parameter to specify if the edits
          should be applied only if all submitted edits succeed. If false,
          the server will apply the edits that succeed even if some of the
          submitted edits fail. If true, the server will apply the edits
          only if all edits succeed. The default value is true.
         :useGlobalIds:Optional parameter which is false by default.
          Requires the service's supportsApplyEditsWithGlobalIds property
          to be true.
         :trueCurveClient:  Optional parameter which is false by default is
          set by client to indicate to the server that client in true curve
          capable.
        """
        url = "{url}/applyEdits".format(url=self._url)
        params = {
            "f" : "json",
            "returnEditMoment" : returnEditMoment,
            "rollbackOnFailure" : rollbackOnFailure,
            "useGlobalIds" : useGlobalIds,
            "trueCurveClient" : trueCurveClient
        }
        if adds:
            params['adds'] = adds
        if deletes:
            params['deletes'] = deletes
        if updates:
            params['updates'] = updates
        if attachments:
            params['attachments'] = attachments
        if gdbVersion:
            params['gdbVersion'] = gdbVersion

        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def attachment(self, oid, attachmentId):
        """
        The Attachment resource represents an individual attachment
        associated with a feature. This resource is available only if the
        layer has advertised that it has attachments. A layer has
        attachments if its hasAttachments property is true.
        The contents of the attachment are streamed to the client.
        Attachments are returned within an attachmentInfos resource. If the
        attachment is not found, an error is returned.

        Parameters:
         :oid:object identifier of the feature
         :attachmentId: unique id of the attachment
        """
        params = {"f" : "json"}
        url = "{url}/{oid}/attachments/{aid}".format(url=self._url,
                                                     oid=oid,
                                                     aid=attachmentId)
        return self._con.get(path=url, params=params)

    #----------------------------------------------------------------------
    def attachment_infos(self,
                        oid,
                        gdbVersion=None,
                        historicMoment=None):
        """
        The attachmentInfos resource returns information about attachments
        associated with a feature. This resource is available only if the
        layer has advertised that it has attachments. A layer has
        attachments if its hasAttachments property is true.
        Each attachment info includes information about the attachment such
        as its ID, content type, size, and name.

        Parameters:
         :oid: object identifier of the feature
         :gdbVersion:Geodatabase version to query. This parameter applies
          only if the isDataVersioned property of the layer is true. If
          this is not specified, query will apply to the published map's
          version.
         :historicMoment:The historic moment to query. This parameter
          applies only if the supportsQueryWithHistoricMoment property of
          the layer being queried is set to true. This setting is provided
          in the layer resource. If historicMoment is not specified, the
          query will apply to the current feature and its attachments.
        """
        params = {"f" : "json"}
        url = "{url}/{oid}/attachments".format(url=self._url,
                                               oid=oid)
        if gdbVersion:
            params['gdbVersion'] = gdbVersion
        if historicMoment:
            params['historicMoment'] = historicMoment
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def calculate(self,
                  where,
                  calcExpression,
                  sqlFormat="standard"):
        """
        The calculate operation is performed on a feature service layer
        resource. It updates the values of one or more fields in an
        existing feature service layer based on SQL expressions or scalar
        values. The calculate operation can only be used if the
        supportsCalculate property of the layer is true.
        Neither the Shape field nor system fields can be updated using
        calculate. System fields include ObjectId and GlobalId.

        Parameters:
         :where:A where clause can be used to limit the updated records.
          Any legal SQL where clause operating on the fields in the layer
          is allowed.
         :calcExpression: The array of field/value info objects that
          contain the field or fields to update and their scalar values or
          SQL expression.
         :sqlFormat: The SQL format for the calcExpression. The expression
          can take one of two formats. It can be either standard SQL92
          (standard), or it can use the native SQL of the underlying
          datastore (native). The default is standard.
        """
        params = {"f" : "json",
                  "where" : where,
                  "calcExpression" : calcExpression,
                  "sqlFormat" : sqlFormat
                  }
        url = "{url}/calculate".format(url=self._url)
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def delete_attachment(self,
                          oid,
                          attachmentIds,
                          returnEditMoments=False,
                          rollbackOnFailure=True):
        """
        This operation deletes attachments associated with a feature (POST
        only). Deleting an attachment is a feature update; it requires the
        Update capability. The deleteAttachments operation is performed on
        a feature service feature resource.

        Parameters:
         :oid: single record object id
         :attachmentIds: The IDs of the attachments to be deleted.
         :returnEditMoment: Optional parameter specifying whether the
          response will report the time edits were applied. If
          returnEditMoment = true, the server will return the time edits
          were applied in the response's editMoment key.
         :rollbackOnFailure:Optional parameter to specify if the edits
          should be applied only if all submitted edits succeed. If false,
          the server will apply the edits that succeed even if some of the
          submitted edits fail. If true, the server will apply the edits
          only if all edits succeed. The default value is true.
        """
        url = "{url}/{oid}/deleteAttachments".format(url=self._url,
                                                     oid=oid)
        params = {
            "f": "json",
            "attachmentIds" : attachmentIds,
            "rollbackOnFailure" : rollbackOnFailure,
            "returnEditMoments": returnEditMoments
        }
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def delete_features(self,
                        objectIds=None,
                        where=None,
                        geometry=None,
                        geometryType=None,
                        inSR=None,
                        spatialRel=None,
                        gdbVersion=None,
                        returnEditMoment=False,
                        rollbackOnFailure=True):
        """
        This operation deletes features in a feature layer or table (POST
        only). The deleteFeatures operation is performed on a feature
        service layer resource.
        The operation returns the results of the edits in an array of edit
        result objects. Each edit result identifies a single edit and
        indicates if the delete was successful or not. If not, it also
        includes an error code and an error description.

        Parameters:
         :objectIds: The object IDs of this layer/table to be deleted.
         :where:A where clause for the query filter. Any legal SQL where
          clause operating on the fields in the layer is allowed. Features
          conforming to the specified where clause will be deleted.
         :geometry: The geometry to apply as the spatial filter. Features
          conforming to the spatial relationship (specified using the
          spatialRel parameter) of this geometry will be deleted. The
          structure of the geometry is the same as the structure of the
          json geometry objects returned by the ArcGIS REST API. In
          addition to the JSON structures, for envelopes and points, you
          can specify the geometry with a simple comma-separated syntax.
         :geometryType: The type of geometry specified by the geometry
          parameter. The geometry type can be an envelope, point, line, or
          polygon. The default geometry type is an envelope.
          Values: esriGeometryPoint | esriGeometryMultipoint |
          esriGeometryPolyline | esriGeometryPolygon | esriGeometryEnvelope
         :inSR: The spatial reference of the input geometry.
         :spatialRel:The spatial relationship to be applied on the input
          geometry while performing the query. The supported spatial
          relationships include intersects, contains, envelope intersects,
          within, and so on. The default spatial relationship is intersects
          (esriSpatialRelIntersects).
          Values: esriSpatialRelIntersects | esriSpatialRelContains |
          esriSpatialRelCrosses | esriSpatialRelEnvelopeIntersects |
          esriSpatialRelIndexIntersects | esriSpatialRelOverlaps |
          esriSpatialRelTouches | esriSpatialRelWithin
         :gdbVersion:Geodatabase version to apply the edits. This parameter
          applies only if the isDataVersioned property of the layer is true
         :returnEditMoment: Optional parameter specifying whether the
          response will report the time edits were applied. If
          returnEditMoment = true, the server will return the time edits
          were applied in the response's editMoment key.
         :rollbackOnFailure:Optional parameter to specify if the edits
          should be applied only if all submitted edits succeed. If false,
          the server will apply the edits that succeed even if some of the
          submitted edits fail. If true, the server will apply the edits
          only if all edits succeed. The default value is true.
        """
        url = "{url}/deleteFeatures".format(url=self._url)
        params = {
            "f": "json"
        }
        if objectIds:
            params['objectIds'] = objectIds
        if where:
            params['where'] = where
        if geometry and geometryType:
            params['geometry'] = geometry
            params['geometryType'] = geometryType
        if inSR:
            params['inSR'] = inSR
        if spatialRel:
            params['spatialRel'] = spatialRel
        if gdbVersion:
            params['gdbVersion'] = gdbVersion
        if returnEditMoment:
            params['returnEditMoment'] = returnEditMoment
        if rollbackOnFailure:
            params['rollbackOnFailure'] = rollbackOnFailure
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def generate_renderer(self,
                          classificationDef,
                          where=None,
                          gdbVersion=None
                          ):
        """
        The generateRenderer operation is performed on a layer/table
        resource. This operation groups data using the supplied
        classificationDef (classification definition) and an optional where
        clause. The result is a renderer object. Use baseSymbol and
        colorRamp to define the symbols assigned to each class. If the
        operation is performed on a table, the result is a renderer object
        containing the data classes and no symbols.

        Parameters:
         :classificationDef:The definition with which the renderer is
          generated.
          Note: Use either the ClassBreaks or UniqueValue classification
          definition.
         :where:A where clause for which the data needs to be classified.
          Any legal SQL where clause operating on the fields in the
          layer/table is allowed.
         :gdbVersion:Geodatabase version to apply the edits. This parameter
          applies only if the isDataVersioned property of the layer is true
        """
        url = "{url}/generateRenderer".format(url=self._url)
        params = {
            "f" : "json",
            "classificationDef" : classificationDef
        }
        if gdbVersion:
            params['gdbVersion'] = gdbVersion
        if where:
            params['where'] = where
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def html_popup(self,
                   oid,
                   gdbVersion=None):
        """
        The htmlPopup resource provides details about the HTML pop-up
        authored by the user using ArcGIS for Desktop. This resource is
        available when a layer resource's htmlPopupType is not
        esriServerHTMLPopupTypeNone.

        Parameters:
         :oid: object id of the popup to get
        """
        url = "{url}/{oid}/htmlPopUp".format(url=self._url,
                                             oid=oid)
        params = {
            "f" : "json"
        }
        if gdbVersion:
            params['gdbVersion'] = gdbVersion
        return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    def image(self, imageId):
        """
        The image resource represents an individual image associated with a
        picture symbol. This resource is available only if the layer
        includes Picture Marker Symbols or Picture Fill Symbols. The url
        property of these symbols should be used as the imageId in the image
        URL. The image bytes are directly streamed to the client.

        Parameters:
         :imageId: id of the symbol to view
        """
        url = "{url}/images/{iid}".format(
            url=self._url,
            iid=imageId
        )
        return self._con.get(path=url)
    #----------------------------------------------------------------------
    def query(self,
              where="1=1",
              objectIds=None,
              geometry=None,
              geometryType="esriGeometryEnvelope",
              inSR=None,
              spatialRel="esriSpatialRelIntersects",
              relationParam=None,
              time=None,
              distance=None,
              units=None,
              outFields="*",
              returnGeometry=True,
              maxAllowableOffset=None,
              geometryPrecision=None,
              outSR=None,
              gdbVersion=None,
              returnDistinctValues=False,
              returnIdsOnly=False,
              returnCountOnly=False,
              returnExtentOnly=False,
              orderByFields=None,
              groupByFieldsForStatistics=None,
              outStatistics=None,
              returnZ=False,
              returnM=False,
              multipathOption=None,
              resultOffset=0,
              resultRecordCount=False,
              quantizationParameters=None,
              returnCentroid=False,
              resultType=None,
              historicMoment=None,
              returnTrueCurves=False,
              sqlFormat="none"
              ):
        """
        Parameters:
         :where: A where clause for the query filter. Any legal SQL where
          clause operating on the fields in the layer is allowed.
         :objectIds: The object IDs of this layer or table to be queried.
         :geometry:The geometry to apply as the spatial filter. The
          structure of the geometry is the same as the structure of the json
          geometry objects returned by the ArcGIS REST API. In addition to
          the JSON structures, for envelopes and points, you can specify the
          geometry with a simpler comma-separated syntax.
         :geometryType: The type of geometry specified by the geometry
          parameter. The geometry type can be an envelope, point, line, or
          polygon. The default geometry type is an envelope.
          Values: esriGeometryPoint | esriGeometryMultipoint |
          esriGeometryPolyline | esriGeometryPolygon | esriGeometryEnvelope
         :inSR: The spatial reference of the input geometry.
         :spatialRel:The spatial relationship to be applied on the input
          geometry while performing the query. The supported spatial
          relationships include intersects, contains, envelope intersects,
          within, and so on. The default spatial relationship is intersects
          (esriSpatialRelIntersects).
          Values: esriSpatialRelIntersects | esriSpatialRelContains |
          esriSpatialRelCrosses | esriSpatialRelEnvelopeIntersects |
          esriSpatialRelIndexIntersects | esriSpatialRelOverlaps |
          esriSpatialRelTouches | esriSpatialRelWithin
         :relationParam: The spatial relate function that can be applied
          while performing the query operation.
         :time:The time instant or the time extent to query.
         :distance: The buffer distance for the input geometries
         :units:The unit for calculating the buffer distance. If unit is
          not specified, the unit is derived from the geometry spatial
          reference. If the geometry spatial reference is not specified,
          the unit is derived from the feature service data spatial
          reference.
          This parameter only applies if supportsQueryWithDistance is true.
          Values: esriSRUnit_Meter | esriSRUnit_StatuteMile |
          esriSRUnit_Foot | esriSRUnit_Kilometer | esriSRUnit_NauticalMile|
          esriSRUnit_USNauticalMile
         :outFields:The list of fields to be included in the returned
          result set. This list is a comma delimited list of field names.
          You can also specify the wildcard "*" as the value of this
          parameter. In this case, the query results include all the field
          values.
         :returnGeometry: If true, the result includes the geometry
          associated with each feature returned. The default is true.
         :maxAllowableOffset:This option can be used to specify the
          maxAllowableOffset to be used for generalizing geometries
          returned by the query operation.
          The maxAllowableOffset is in the units of outSR. If outSR is not
          specified, maxAllowableOffset is assumed to be in the unit of the
          spatial reference of the map.
         :geometryPrecision:This option can be used to specify the number
          of decimal places in the response geometries returned by the
          Query operation.
          This applies to X and Y values only (not m or z-values).
         :outSR:The spatial reference of the returned geometry.
         :gdbVersion:Geodatabase version to query. This parameter applies
          only if the isDataVersioned property of the layer is true. If
          this is not specified, query will apply to the published map's
          version.
         :returnDistinctValues:If true, it returns distinct values based on
          the fields specified in outFields. This parameter applies only if
          the supportsAdvancedQueries property of the layer is true.
         :returnIdsOnly:If true, the response only includes an array of
          object IDs. Otherwise, the response is a feature set. The default
          is false.
          While there is a limit to the number of features included in the
          feature set response, there is no limit to the number of object
          IDs returned in the ID array response. Clients can exploit this
          to get all the query conforming object IDs by specifying
          returnIdsOnly=true and subsequently requesting feature sets for
          subsets of object IDs.
          When objectIds are specified, setting this parameter to true is
          invalid.
         :returnCountOnly:If true, the response only includes the count
          (number of features/records) that would be returned by a query.
          Otherwise, the response is a feature set. The default is false.
          This option supersedes the returnIdsOnly parameter. If
          returnCountOnly = true, the response will return both the count
          and the extent.
         :returnExtentOnly:If true, the response only includes the extent
          of the features that would be returned by the query. If
          returnCountOnly=true, the response will return both the count and
          the extent. The default is false. This parameter applies only if
          the supportsReturningQueryExtent property of the layer is true.
         :orderByFields:One or more field names on which the features or
          records need to be ordered. Use ASC or DESC for ascending or
          descending, respectively, following every field to control the
          ordering.
         :groupByFieldsForStatistics:One or more field names on which the
          values need to be grouped for calculating the statistics.
         :outStatistics:The definitions for one or more field-based
          statistics to be calculated.
         :returnZ:If true, Z values are included in the results if the
          features have Z values. Otherwise, Z values are not returned. The
          default is false.
         :returnM: If true, M values are included in the results if the
          features have M values. Otherwise, M values are not returned. The
          default is false.
         :multipathOption:This option dictates how the geometry of a
          multipatch feature will be returned.
         :resultOffset:This option can be used for fetching query results
          by skipping the specified number of records and starting from the
          next record (that is, resultOffset + 1th). The default is 0.
          This parameter only applies if supportsPagination is true.
          You can use this option to fetch records that are beyond
          maxRecordCount.
         :resultRecordCount:This option can be used for fetching query
          results up to the resultRecordCount specified. When resultOffset
          is specified but this parameter is not, the map service defaults
          it to maxRecordCount. The maximum value for this parameter is the
          value of the layer's maxRecordCount property.
          This parameter only applies if supportsPagination is true.
         :quantizationParameters:Used to project the geometry onto a virtual
          grid, likely representing pixels on the screen.
         :returnCentroid:Used to return the geometry centroid associated
          with each feature returned. If true, the result includes the
          geometry centroid. The default is false.
         :resultType:The resultType parameter can be used to control the
          number of features returned by the query operation.
          Values: none | standard | tile
         :historicMoment:The historic moment to query. This parameter
          applies only if the layer is archiving enabled and the
          supportsQueryWithHistoricMoment property is set to true. This
          property is provided in the layer resource.
          If historicMoment is not specified, the query will apply to the
          current features.
         :returnTrueCurves:Optional parameter which is false by default.
          When set to true, returns true curves in output geometries.
          When set to false, curves are converted to densified polylines or
          polygons.
         :sqlFormat:The sqlFormat parameter can be either standard SQL92
          standard or it can use the native SQL of the underlying datastore
          native. The default is none which means the sqlFormat depends on
          useStandardizedQuery parameter.
          Values: none | standard | native
        """
        params = {"f": "json"}
        url = "{url}/query".format(url=self._url)
        if units:
            params['units'] = units
        if distance:
            params['distance'] = distance
        if returnExtentOnly:
            params['returnExtentOnly'] = returnExtentOnly
        if outFields:
            params['outFields'] = outFields
        if where:
            params['where'] = where
        if objectIds:
            params['objectIds'] = objectIds
        if geometry:
            params['geometry'] = geometry
        if geometryType:
            params['geometryType'] = geometryType
        if inSR:
            params['inSR'] = inSR
        if spatialRel:
            params['spatialRel'] = spatialRel
        if time:
            params['time'] = time
        if relationParam:
            params['relationParam'] = relationParam
        if returnGeometry == False:
            params['returnGeometry'] = returnGeometry
        if maxAllowableOffset:
            params['maxAllowableOffset'] = maxAllowableOffset
        if geometryPrecision:
            params['geometryPrecision'] = geometryPrecision
        if outSR:
            params['outSR'] = outSR
        if gdbVersion:
            params['gdbVersion'] = gdbVersion
        if returnDistinctValues:
            params['returnDistinctValues'] = returnDistinctValues
        if returnIdsOnly:
            params['returnIdsOnly'] = returnIdsOnly
        if returnCountOnly:
            params['returnCountOnly'] = returnCountOnly
        if orderByFields:
            params['orderByFields'] = orderByFields
        if groupByFieldsForStatistics:
            params['groupByFieldsForStatistics'] = groupByFieldsForStatistics
        if outStatistics:
            params['outStatistics'] = outStatistics
        if returnZ:
            params['returnZ']= returnZ
        if returnM:
            params['returnM'] = returnM
        if multipathOption:
            params['multipathOption'] = multipathOption
        if resultOffset:
            params['resultOffset'] = resultOffset
        if resultRecordCount:
            params['resultRecordCount'] = resultRecordCount
        if quantizationParameters:
            params['quantizationParameters'] = quantizationParameters
        if returnCentroid:
            params['returnCentroid'] = returnCentroid
        if resultType:
            params['resultType'] = resultType
        if historicMoment:
            params['historicMoment'] = historicMoment
        if returnTrueCurves:
            params['returnTrueCurves'] = returnTrueCurves
        if sqlFormat:
            params['sqlFormat'] = sqlFormat
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def query_attachments(self,
                          objectIds,
                          globalIds=None,
                          definitionExpression=None,
                          attachmentTypes=None,
                          size=None,
                          resultOffset=None,
                          resultRecordCount=None
                          ):
        """
        The Query Attachments operation is performed on a feature service
        layer resource. The result of this operation are attachments
        grouped by the source feature object Ids and global ids (if exist).

        Parameters:
         :objectIds:The object IDs of this layer/table to be queried.
         :globalIds:The global IDs of this layer/table to be queried.
         :definitionExpression:The definition expression to be applied to
          the related layer/table. From the list of records that are related
          to the specified objectIds, only those records that conform to
          this expression will be returned.
         :attachmentTypes:The file format that is supported by query
          attachment.
         :size:The file size of the attachment is specified in bytes. You
          can enter a file size range (1000,15000) to query for attachments
          with the specified range.
         :resultOffset:This option fetches query results by skipping a
          specified number of records. The query results start from the
          next record (i.e., resultOffset + 1). The default value is 0.
          This parameter only applies when supportPagination is true.
          You can use this option to fetch records that are beyond
          maxRecordCount.
         :resultRecordCount:This option fetches query results up to the
          resultRecordCount specified. When resultOffset is specified and
          this parameter is not, the feature service defaults to the
          maxRecordCount The maximum value for this parameter is the value
          of the layer's maxRecordCount property.
          This parameter only applies if supportPagination is true.
        """
        url = "{url}/queryAttachments".format(url=self._url)
        params = {
            "f" : "json"
        }
        if objectIds:
            params['objectIds'] = objectIds
        if globalIds:
            params['globalIds'] = globalIds
        if definitionExpression:
            params['definitionExpression'] = definitionExpression
        if attachmentTypes:
            params['attachmentTypes'] = attachmentTypes
        if size:
            params['size'] = size
        if resultOffset:
            params['resultOffset'] = resultOffset
        if resultRecordCount:
            params['resultRecordCount'] = resultRecordCount
        return self._con.get(path=url, params=params)
    #----------------------------------------------------------------------
    def query_related_records(self,
                              objectIds,
                              relationshipId,
                              outFields="*",
                              definitionExpression=None,
                              returnGeometry=True,
                              maxAllowableOffset=None,
                              geometryPrecision=None,
                              resultOffset=0,
                              resultRecordCount=None,
                              outSR=None,
                              gdbVersion=None,
                              historicMoment=None,
                              returnZ=False,
                              returnM=False,
                              returnTrueCurves=False,
                              orderByFields=None,
                              returnCountOnly=False
                              ):
        """
         :objectIds:The object IDs of the layer/table to be queried.
          Records related to these object IDs will be queried.
         :relationshipId:The ID of the relationship to be queried. The
          relationships that this layer/table participates in are included
          in the Feature Service Layer resource response. Records in
          tables/layers corresponding to the related table/layer of the
          relationship are queried.
         :outFields:The list of fields to be included in the returned
          result set. This list is a comma delimited list of field names.
          You can also specify the wildcard "*" as the value of this
          parameter. In this case, the query results include all the field
          values.
         :definitionExpression:The definition expression to be applied to
          the related table/layer. From the list of objectIds, only those
          records that conform to this expression are queried for related
          records.
         :returnGeometry: If true, the result includes the geometry
          associated with each feature returned. The default is true.
         :maxAllowableOffset:This option can be used to specify the
          maxAllowableOffset to be used for generalizing geometries
          returned by the query operation.
          The maxAllowableOffset is in the units of outSR. If outSR is not
          specified, maxAllowableOffset is assumed to be in the unit of the
          spatial reference of the map.
         :geometryPrecision:This option can be used to specify the number
          of decimal places in the response geometries returned by the
          Query operation.
          This applies to X and Y values only (not m or z-values).
         :resultOffset:This option can be used for fetching query results
          by skipping the specified number of records and starting from the
          next record (that is, resultOffset + 1th). The default is 0.
         :resultRecordCount:This option can be used for fetching query
          results up to the resultRecordCount specified. When resultOffset
          is specified but this parameter is not, the map service defaults
          it to maxRecordCount. The maximum value for this parameter is the
          value of the layer's maxRecordcountresultOffset property.
         :outSR:The spatial reference of the returned geometry.
         :gdbVersion:Geodatabase version to query. This parameter applies
          only if the isDataVersioned property of the layer is true. If
          this is not specified, query will apply to the published map's
          version.
         :historicMoment:The historic moment to query. This parameter
          applies only if the layer is archiving enabled and the
          supportsQueryWithHistoricMoment property is set to true. This
          property is provided in the layer resource.
          If historicMoment is not specified, the query will apply to the
          current features.
         :returnTrueCurves:Optional parameter which is false by default.
          When set to true, returns true curves in output geometries.
          When set to false, curves are converted to densified polylines or
          polygons.
         :returnZ:If true, Z values are included in the results if the
          features have Z values. Otherwise, Z values are not returned. The
          default is false.
         :returnM: If true, M values are included in the results if the
          features have M values. Otherwise, M values are not returned. The
          default is false.
         :orderByFields:
         :returnCountOnly:
        """
        url = "{url}/queryRelatedRecords".format(url=self._url)
        params = {"f" : "json"}

        gdbVersion=None,
        historicMoment=None,
        returnZ=False,
        returnM=False,
        returnTrueCurves=False,
        orderByFields=None,
        returnCountOnly=False
        if objectIds:
            params['objectIds'] = objectIds
        if relationshipId:
            params['relationshipId'] = relationshipId
        if outFields:
            params['outFields'] = outFields
        if definitionExpression:
            params['definitionExpression'] = definitionExpression
        if returnGeometry == False:
            params['returnGeometry'] = returnGeometry
        if maxAllowableOffset:
            params['maxAllowableOffset'] = maxAllowableOffset
        if geometryPrecision:
            params['geometryPrecision'] = geometryPrecision
        if resultOffset:
            params['resultOffset'] = resultOffset
        if resultRecordCount:
            params['resultRecordCount'] = resultRecordCount
        if outSR:
            params['outSR'] = outSR
        if gdbVersion:
            params['gdbVersion'] = gdbVersion
        if historicMoment:
            params['historicMoment'] = historicMoment
        if returnM:
            params['returnM'] = returnM
        if returnZ:
            params['returnZ'] = returnZ
        if returnTrueCurves:
            params['returnTrueCurves'] = returnTrueCurves
        if orderByFields:
            params['orderByFields'] = orderByFields
        if returnCountOnly:
            params['returnCountOnly'] = returnCountOnly
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def update_attachment(self,
                          oid,
                          attachmentId,
                          attachment=None,
                          gdbVersion=None,
                          returnEditMoment=False,
                          uploadId=None):
        """
        This operation updates an attachment associated with a feature
        (POST only). Updating an attachment is a feature update, it
        requires the Update capability. The updateAttachment operation is
        performed on a feature service feature resource.
        Since this request uploads a file, it must be a multipart request
        pursuant to IETF RFC1867.
        This operation is available only if the layer has advertised that
        it has attachments. A layer has attachments if its hasAttachments
        property is true.
        See the Limiting upload file size and file types section of Uploads
        to learn more about default file size and file type limitations
        imposed for attachments.
        The result of this operation is an array of edit result objects.
        Each edit result indicates whether or not the edit was successful.
        If successful, the objectId of the result is the ID of the updated
        attachment. If unsuccessful, it also includes an error code and an
        error description.

        Parameter:
         :oid: record to update
         :attachmentId:The ID of the attachment to be updated.
         :attachment:The file to be uploaded as the updated feature
          attachment.
         :gdbVersion:Geodatabase version to apply the edits. This parameter
          applies only if the isDataVersioned property of the layer is true.
         :returnEditMoment:Optional parameter specifying whether the
         response will report the time attachments were updated. If
         returnEditMoment = true, the server will report the time in the
         response's editMoment key. The default value is false.
         :uploadId:The ID of the attachment that has already been uploaded
          to the server. This parameter only applies if the
          supportsAttachmentsByUploadId property of the layer is true.
        """
        params = {
            "f" : "json",
            "returnEditMoment" : returnEditMoment,
            "attachmentId" : attachmentId
        }
        url = "{url}/{oid}/updateAttachment".format(url=self._url,
                                                    oid=oid)
        if uploadId:
            params['uploadId'] = uploadId
        if gdbVersion:
            params['gdbVersion'] = gdbVersion
        if attachment:
            files = {
                "attachment": attachment
            }
        else:
            files = {}
        return self._con.post(path=url,
                              postdata=params,
                              files=files)
    #----------------------------------------------------------------------
    def update_features(self,
                        features,
                        gdbVersion=None,
                        returnEditMoment=False,
                        rollbackOnFailure=True,
                        trueCurveClient=False
                        ):
        """

        Parameters:
         :features:The array of features to be updated. The structure of
          each feature in the array is the same as the structure of the
          json feature object returned by the ArcGIS REST API.
         :gdbVersion:Geodatabase version to apply the edits. This
          parameter applies only if the isDataVersioned property of the
          layer is true. If the gdbVersion parameter is not specified,
          edits are made to the published map’s version.
         :returnEditMoment:Optional parameter specifying whether the
          response will report the time features were updated. If
          returnEditMoment = true, the server will report the time in the
          response's editMoment key. The default value is false.
         :rollbackOnFailure:Optional parameter to specify if the edits
          should be applied only if all submitted edits succeed. If false,
          the server will apply the edits that succeed even if some of the
          submitted edits fail. If true, the server will apply the edits
          only if all edits succeed. The default value is true.
         :trueCurveClient:Optional parameter which is false by default is
          set by client to indicate to the server that client in true curve
          capable.
          When set to true by client, indicates to the server that true
          curves geometries should be downloaded from and that geometries
          containing true curves should be consumed by the feature service,
          without converting curves to densified polylines or polygons.
          When set to false by client, indicates to the server that client
          is not true curves capable and hence, curves are converted to
          densified polylines or polygons.
        """
        url = "{url}/updateFeatures".format(url=self._url)
        params = {
            "f" : "json",
            "features" : features,
            "rollbackOnFailure" : rollbackOnFailure,
            "trueCurveClient": trueCurveClient,
            "returnEditMoment" : returnEditMoment
        }
        if gdbVersion:
            params['gdbVersion'] = gdbVersion
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def validate_sql(self,
                     sql,
                     sqlType="where"
                     ):
        """
        The validateSQL operation validates an SQL-92 expression or WHERE
        clause.
        The validateSQL operation ensures that an SQL-92 expression, such
        as one written by a user through a user interface, is correct
        before performing another operation that uses the expression. For
        example, validateSQL can be used to validate information that is
        subsequently passed in as part of the where parameter of the
        calculate operation.
        validateSQL also prevents SQL injection. In addition, all table and
        field names used in the SQL expression or WHERE clause are
        validated to ensure they are valid tables and fields.
        **Note**
        The validateSQL operation is only supported in ArcGIS Online hosted
        feature services.
        """
        url = "{url}/validateSQL".format(url=self._url)
        params = {
            "f" : "json",
            "sql" : sql,
            "sqlType" : sqlType
        }
        return self._con.get(path=url,
                             params=params)

########################################################################
class TableLayer(FeatureLayer):
    """Table object is exactly like FeatureLayer object"""
    pass
########################################################################
class TiledService(BaseServer):
    """
       AGOL Tiled Map Service
    """
    _con = None
    _url = None
    _json_dict = None
########################################################################
class SchematicLayer(FeatureLayer):
    pass
########################################################################
class RasterLayer(FeatureLayer):
    pass
########################################################################
class GroupLayer(FeatureLayer):
    pass
########################################################################
