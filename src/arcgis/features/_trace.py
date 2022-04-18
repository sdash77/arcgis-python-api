from __future__ import annotations
from typing import Any, Optional, Union
from arcgis import env
from arcgis._impl.common._mixins import PropertyMap

########################################################################
class TraceNetworkManager(object):
    """
    The Trace Network Service exposes analytic capabilities (tracing)
    as well as validation of network topology.

    =====================   ===========================================
    **Inputs**              **Description**
    ---------------------   -------------------------------------------
    url                     Required String. The web endpoint to the trace service.
    ---------------------   -------------------------------------------
    version                 Required Version. The `Version` class where the branch version will take place.
    ---------------------   -------------------------------------------
    gis                     Optional GIS. The `GIS` connection object.
    =====================   ===========================================


    """

    _con = None
    _gis = None
    _url = None
    _version = None
    _property = None
    _version_guid = None
    _version_name = None
    # ----------------------------------------------------------------------
    def __init__(self, url, version, gis=None):
        """Constructor"""
        if gis is None:
            gis = env.active_gis
        self._gis = gis
        self._con = gis._portal.con
        self._url = url
        self._version = version
        self._version_guid = version._guid
        self._version_name = version.properties.versionName

    # ----------------------------------------------------------------------
    def _init(self):
        """initializer"""
        try:
            res = self._con.get(self._url, {"f": "json"})
            self._property = PropertyMap(res)
        except Exception as e:
            self._property = PropertyMap({})

    # ----------------------------------------------------------------------
    @property
    def properties(self):
        """returns the properties for the service"""
        if self._property is None:
            self._init()
        return self._property

    # ----------------------------------------------------------------------
    def trace(
        self,
        locations: list[dict],
        trace_type: str,
        moment: Optional[str] = None,
        configuration: Optional[dict] = None,
        result_types: Optional[list[dict]] = None,
        run_async: bool = False,
    ):
        """
        A trace refers to a preconfigured algorithm that systematically
        travels a network to return results. Multiple parameters and properties
        are provided with the trace operation that support various analytic workflows.
        All traces use the network topology to read cached information about network features.
        This can improve performance of complex traces on large networks.
        Trace results are not guaranteed to accurately represent a trace network when
        dirty areas are present. The network topology must be validated to ensure that it
        reflects the most recent edits or updates made to the network.

        .. note::
            The active portal account must be licensed with the ArcGIS Trace
            Network user type extention to use this operation.

        ====================    ==================================================
        **Arguments**           **Description**
        --------------------    --------------------------------------------------
        locations               Required list of dictionaries. The locations for
                                starting points and barriers. An empty array must
                                be used when performing a subnetwork trace if a
                                subnetworkName is provided as part of the
                                `configuration`—for example, `locations=[]`.


                                The location is ignored by the trace if the following
                                required properties are not defined:
                                * `percentAlong` : required for edge features and objects.
                                * `terminalID` : required for junction features and objects.


                                .. code-block:: python
                                    [{
                                        "traceLocationType" : "startingPoint" | "barrier",
                                        "globalId" : <guid>,
                                        “percentAlong” : <double>, // optional
                                    }]
        --------------------    --------------------------------------------------
        trace_type              Required string. Specifies the core algorithm that
                                will be executed to analyze the network. Can be
                                configured using the `configuration` parameter.

                                `Values: 'connected' | 'subnetwork' | 'subnetworkController' |
                                'upstream' | 'downstream' | 'loops' | 'shortestPath' |
                                'isolation'`
        --------------------    --------------------------------------------------
        moment                  Optional Integer. Specifies the session moment. This
                                should only be specified if you do not want to use
                                the current moment.

                                Example: moment = <Epoch time in milliseconds>
        --------------------    --------------------------------------------------
        configuration           Optional dictionary. Specifies the collection of
                                trace configuration properties. Depending on the
                                `trace_type`, some properties are required.

                                To see all configuration properties see:
                                `Trace Configuration Properties
                                <https://developers.arcgis.com/rest/services-reference/enterprise/trace-trace-network-server-.htm#GUID-F0C932FD-B403-4223-9B00-E44D156C7DF9/>`_
        --------------------    --------------------------------------------------
        result_types            Optional parameter specifying hte types of results
                                to return.

                                .. code-block::
                                    [{
                                        "type" : "elements" | "aggregatedGeometry" | "connectivity",
                                        "includeGeometry" : true | false,
                                        "includePropagatedValues": true | false,
                                        "networkAttributeNames" :["attribute1Name","attribute2Name",...],
                                        "diagramTemplateName": <value>,
                                        "resultTypeFields":[{"networkSourceId":<long>,"fieldname":<value>},...]
                                    },...]

                                .. note::
                                    ArcGIS Enterprise 10.9.1 or later is required when
                                    using the `connectivity` type.
        ====================    ==================================================

        :return: If `asynchronous = True` then the status URL is returned for the job. Otherwise,
        a Dictionary of the Trace Results is returned.
        """
        url = "%s/trace" % self._url

        params = {
            "f": "json",
            "gdbVersion": self._version_name,
            "sessionId": self._version_guid,
            "traceType": trace_type,
            "moment": moment,
            "traceLocations": locations,
            "traceConfiguration": configuration,
            "resultTypes": result_types,
            "async": run_async,
        }
        return self._con.post(url, params)

    # ----------------------------------------------------------------------
    def query_network_moments(
        self,
        moments_to_return: Optional[list[str]] = ["all"],
        moment: Optional[str] = None,
    ):
        """
        The `query_network_moments` operation returns the moments related
        to the network topology and operations against the topology. This
        includes when the topology was initially enabled, when it was last
        validated, when the topology was last disabled (and later enabled),
        and when the definition of the trace network was last modified.

        ====================================        ====================================================================
        **Argument**                                **Description**
        ------------------------------------        --------------------------------------------------------------------
        moments_to_return                           Optional List of Strings. Represents the collection of validate moments to
                                                    return. Default is all.

                                                    `Values: ["initialEnableTopology" | "fullValidateTopology" |
                                                            "partialValidateTopology" | "enableTopology" | "disableTopology" |
                                                            "definitionModification" | "indexUpdate" | "all" ]`
        ------------------------------------        --------------------------------------------------------------------
        moment                                      Optional Epoch in Time in Seconds.
                                                    Example: `moment=1603109606`
        ====================================        ====================================================================

        """
        url = "%s/queryNetworkMoments" % self._url
        params = {
            "f": "json",
            "gdbVersion": self._version_name,
            "sessionId": self._version_guid,
            "momentsToReturn": moments_to_return,
            "moment": moment,
        }
        return self._con.post(url, params)

    # ----------------------------------------------------------------------
    def validate_topology(
        self,
        envelope: dict[str, Any],
        return_edits: bool = False,
    ):
        """
        Validating the network topology for a trace network maintains
        consistency between feature editing space and network topology space.
        Validating a network topology may include all or a subset of the
        dirty areas present in the network. Validation of network topology
        is supported synchronously and asynchronously.

        ====================================        ====================================================================
        **Argument**                                **Description**
        ------------------------------------        --------------------------------------------------------------------
        envelope                                    Required Dictionary. The envelope of the area to validate.

                                                    .. code-block:: python
                                                        {
                                                            "xmin": <minimum x-coordinate>,
                                                            "ymin": <minimum y-coordinate>,
                                                            "xmax": <maximum x-coordinate>,
                                                            "ymax": <maximum y-coordinate>,
                                                            "spatialReference": {
                                                            "wkid": <spatial reference well-known identifier>,
                                                            "latestWkid": <the current wkid value associated with the wkid>
                                                            }
                                                        }
        ------------------------------------        --------------------------------------------------------------------
        return_edits                                Optional Boolean. Returned results are organized in a layer-by-layer fashion.
                                                    If `return_edits` is set to True, each layer may have edited features
                                                    returned in an editedFeatures object.
                                                    The editedFeatures object returns full features including the original
                                                    features prior to delete; the original and current features for updates;
                                                    and the current rows for inserts, which may contain implicit changes
                                                    (for example, as a result of a calculation rule).

                                                    The response includes no editedFeatures and 'exceededTransferLimit = true'
                                                    if the count of edited features to return is more than the maxRecordCount.
                                                    If clients are using this parameter to maintain a cache, they should
                                                    invalidate the cache when exceededTransferLimit = true is returned.
                                                    If the server encounters an error when generating the list
                                                    of edits is the response, exceededTransferLimit = true is also returned.

                                                    Edited features are returned in the spatial reference
                                                    of the feature service as defined by the service's spatialReferenceobject
                                                    or by the spatialReference of the layer's extent object.
        ====================================        ====================================================================

        :return: Dictionary indicating 'success' or 'error'

        """
        url = "%s/validateNetworkTopology" % self._url
        params = {
            "f": "json",
            "gdbVersion": self._version_name,
            "sessionId": self._version_guid,
            "validateArea": envelope,
            "returnEdits": return_edits,
        }
        return self._con.post(url, params)

    # ----------------------------------------------------------------------
    def trace_configurations(self):
        """
        The `trace_configurations` resource provides access to all trace
        configuration operations for a trace network.
        It is returned as an array of named trace configurations with the creator,
        name, and global ID for each.
        """

        url = "%s/traceConfigurations"
        params = {"f": "json"}
        return self._con.post(url, params)

    # ----------------------------------------------------------------------
    def alter_trace_configurations(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        trace_type: str = "connected",
        trace_config: Optional[dict] = {},
        result_types: Optional[list[dict]] = None,
        tags: Optional[list[str]] = None,
    ):
        """
        The alter operation provides the ability to alter a single named
        trace configuration. A named trace configuration can only be altered
        by an administrator or the creator of the configuration.
        For example, you can update an existing trace configuration to
        accommodate changes in the network or address incorrectly set parameters
        without the need to delete and re-create a trace configuration.
        This enables existing map services to continue use of the named trace
        configuration without requiring the map to be republished.

        ======================      ===============================================
        **Argument**                **Description**
        ----------------------      -----------------------------------------------
        name                        Optional String. The altered name of the trace
                                    configuration.
        ----------------------      -----------------------------------------------
        description                 Optional String. Specify the altered description
                                    of the trace configuration.
        ----------------------      -----------------------------------------------
        trace_type                  Optional String. Specify the core algorithm that
                                    will be used to analyze the network. Trace types
                                    can be configured using the `trace_config` parameter.

                                    `Values: "connected" | "subnetwork" | "upstream" |
                                    "subnetworkController" | "downstream" | "loops" |
                                    "shortenPath" | "isolation"`
        ----------------------      -----------------------------------------------
        trace_config                Optional Dictionary. Specify the collection of
                                    altered trace configuration properties.

                                    See: `Properties <https://developers.arcgis.com/rest/services-reference/enterprise/trace-trace-network-server-.htm#GUID-F0C932FD-B403-4223-9B00-E44D156C7DF9/>`_
        ----------------------      -----------------------------------------------
        result_types                Optional List of Dictionary. Specify the altered
                                    types of results to return.

                                    .. code-block:: python
                                        [{
                                            "type" : "elements" | "aggregatedGeometry",
                                            "includeGeometry" : true | false,
                                            "includePropagatedValues": true | false,
                                            "networkAttributeNames" :["attribute1Name","attribute2Name",...],
                                            "diagramTemplateName": <value>,
                                            "resultTypeFields":[{"networkSourceId":<long>,"fieldname":<value>},...]
                                        },...]

        ----------------------      -----------------------------------------------
        tags                        Optional List of String(s). Specify the altered
                                    user-provided tags.
        ======================      ===============================================

        """

        url = "%s/traceConfigurations/alter"
        params = {
            "f": "json",
            "gdbVersion": self._version_name,
            "name": name,
            "description": description,
            "traceType": trace_type,
            "traceConfiguration": trace_config,
            "resultTypes": result_types,
            "tags": tags,
        }
        return self._con.post(url, params)

    # ----------------------------------------------------------------------
    def create_trace_configurations(
        self,
        name: str,
        trace_type: str,
        trace_config: dict,
        description: Optional[str] = None,
        result_types: Optional[list[dict]] = None,
        tags: Optional[list[str]] = None,
    ):
        """
        The create operation on the traceConfigurations resource provides the
        ability to create a single named trace configuration. Named trace
        configurations store the properties of a complex trace in a trace
        network and can be shared through a map service consumed by a web map
        or field app. Multiple parameters and properties are provided with
        the create operation that support the analytic workflows associated
        with the trace operation.

        ======================      ===============================================
        **Argument**                **Description**
        ----------------------      -----------------------------------------------
        name                        Required String. The altered name of the trace
                                    configuration.
        ----------------------      -----------------------------------------------
        trace_type                  Required String. Specify the core algorithm that
                                    will be used to analyze the network. Trace types
                                    can be configured using the `trace_config` parameter.

                                    `Values: "connected" | "upstream" | "downstream" |
                                    "shortenPath"`
        ----------------------      -----------------------------------------------
        trace_config                Required Dictionary. Specify the collection of
                                    altered trace configuration properties.

                                    See: `Properties <https://developers.arcgis.com/rest/services-reference/enterprise/trace-trace-network-server-.htm#GUID-F0C932FD-B403-4223-9B00-E44D156C7DF9/>`_
        ----------------------      -----------------------------------------------
        description                 Optional String. Specify the altered description
                                    of the trace configuration.
        ----------------------      -----------------------------------------------
        result_types                Optional List of Dictionary. Specify the altered
                                    types of results to return.

                                    .. code-block:: python
                                        [{
                                            "type" : "elements" | "aggregatedGeometry",
                                            "includeGeometry" : true | false,
                                            "includePropagatedValues": true | false,
                                            "networkAttributeNames" :["attribute1Name","attribute2Name",...],
                                            "diagramTemplateName": <value>,
                                            "resultTypeFields":[{"networkSourceId":<long>,"fieldname":<value>},...]
                                        },...]

        ----------------------      -----------------------------------------------
        tags                        Optional List of String(s). Specify the altered
                                    user-provided tags.
        ======================      ===============================================

        """
        url = "%s/traceConfigurations/create"
        params = {
            "f": "json",
            "gdbVersion": self._version_name,
            "name": name,
            "description": description,
            "traceType": trace_type,
            "traceConfiguration": trace_config,
            "resultTypes": result_types,
            "tags": tags,
        }
        return self._con.post(url, params)

    # ----------------------------------------------------------------------
    def delete_trace_configurations(self, global_ids: list[str]):
        """
        The delete operation provides the ability to delete one or more named
        trace configurations in a trace network. A named trace configuration
        can only be deleted by an administrator or its creator.
        """
        url = "%s/traceConfigurations/delete"
        params = {
            "f": "json",
            "globalIds": global_ids,
        }
        return self._con.post(url, params)

    # ----------------------------------------------------------------------
    def query_trace_configurations(
        self,
        global_ids: Optional[list[str]] = None,
        creators: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
        names: Optional[list[str]] = None,
    ):
        """
        The query operation returns all properties from one or more
        named trace configurations in a trace network.

        ========================    ===========================================
        **Argument**                **Description**
        ------------------------    -------------------------------------------
        global_ids                  Optional list of strings. Specify the global
                                    IDs of the named trace configs to be queried.
        ------------------------    -------------------------------------------
        creators                    Optional list of strings. The creators of
                                    the named trace configurations to be queried.
        ------------------------    -------------------------------------------
        tags                        Optional list of strings. The user tags of
                                    the named trace configurations to be queried.
        ------------------------    -------------------------------------------
        names                       Optional list of strings. The names of the
                                    named trace configurations to be queried.
        ========================    ===========================================
        """
        url = "%s/traceConfigurations/query"
        params = {
            "f": "json",
            "globalIds": global_ids,
            "creators": creators,
            "tags": tags,
            "names": names,
        }
        return self._con.post(url, params)

    # ----------------------------------------------------------------------
