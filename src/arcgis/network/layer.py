from arcgis.gis import Layer, _GISResource


class NetworkLayer(Layer):
    """
    NetworkLayer represents a single network layer. It provides basic
    information about the network layer such as its name, type, and network
    classes. Additionally, depending on the layer type, it provides different
    pieces of information.

    It is a base class for RouteLayer, ServiceAreaLayer, and
    ClosestFacilityLayer.
    """
    def retrieve_travel_modes(self):
        """identify all the valid travel modes that have been defined on the
        network dataset or in the portal if the GIS server is federated"""
        url = self._url + "/retrieveTravelModes"
        params = {"f":"json"}
        return self._con.get(path=url,
                         params=params, token=self._token)


class RouteLayer(NetworkLayer):
    """
    The Route Layer which has common properties of Network Layer
    as well as some attributes unique to Route Network Layer only.
    """
    def solve(self,stops,
              barriers=None,
              polylineBarriers=None,
              polygonBarriers=None,
              travelMode=None,
              attributeParameterValues=None,
              returnDirections=None,
              returnRoutes=True,
              returnStops=False,
              returnBarriers=False,
              returnPolylineBarriers=True,
              returnPolygonBarriers=True,
              outSR=None,
              ignoreInvalidLocations=True,
              outputLines=None,
              findBestSequence=False,
              preserveFirstStop=True,
              preserveLastStop=True,
              useTimeWindows=False,
              startTime=None,
              startTimeIsUTC=False,
              accumulateAttributeNames=None,
              impedanceAttributeName=None,
              restrictionAttributeNames=None,
              restrictUTurns=None,
              useHierarchy=True,
              directionsLanguage=None,
              directionsOutputType=None,
              directionsStyleName=None,
              directionsLengthUnits=None,
              directionsTimeAttributeName=None,
              outputGeometryPrecision=None,
              outputGeometryPrecisionUnits=None,
              returnZ=False
              ):
        """The solve operation is performed on a network layer resource.
        The solve operation is supported on a network layer whose layerType
        is esriNAServerRouteLayer. You can provide arguments to the solve
        route operation as query parameters.
        Inputs:
            stops - The set of stops loaded as network locations during analysis.
                    Stops can be specified using a simple comma / semi-colon
                    based syntax or as a JSON structure. If stops are not
                    specified, preloaded stops from the map document are used in
                    the analysis.
            barriers - The set of barriers loaded as network locations during
                       analysis. Barriers can be specified using a simple comma
                       / semi-colon based syntax or as a JSON structure. If
                       barriers are not specified, preloaded barriers from the
                       map document are used in the analysis. If an empty json
                       object is passed ('{}') preloaded barriers are ignored.
            polylineBarriers - The set of polyline barriers loaded as network
                               locations during analysis. If polyline barriers
                               are not specified, preloaded polyline barriers
                               from the map document are used in the analysis.
                               If an empty json object is passed ('{}')
                               preloaded polyline barriers are ignored.
            polygonBarriers - The set of polygon barriers loaded as network
                              locations during analysis. If polygon barriers
                              are not specified, preloaded polygon barriers
                              from the map document are used in the analysis.
                              If an empty json object is passed ('{}') preloaded
                              polygon barriers are ignored.

            travelMode - Travel modes provide override values that help you
                         quickly and consistently model a vehicle or mode of
                         transportation. The chosen travel mode must be
                         preconfigured on the network dataset that the routing
                         service references.
            attributeParameterValues - A set of attribute parameter values that
                                       can be parameterized to determine which
                                       network elements can be used by a vehicle.
            returnDirections - If true, directions will be generated and returned
                               with the analysis results. Default is true.
            returnRoutes - If true, routes will be returned with the analysis
                           results. Default is true.
            returnStops -  If true, stops will be returned with the analysis
                           results. Default is false.
            returnBarriers -  If true, barriers will be returned with the analysis
                              results. Default is false.
            returnPolylineBarriers -  If true, polyline barriers will be returned
                                      with the analysis results. Default is false.
            returnPolygonBarriers - If true, polygon barriers will be returned with
                                    the analysis results. Default is false.
            outSR - The spatial reference of the geometries returned with the
                    analysis results.
            ignoreInvalidLocations - If true, the solver will ignore invalid
                                     locations. Otherwise, it will raise an error.
                                     The default is as defined in the network layer.
            outputLines - The type of output lines to be generated in the result.
                          The default is as defined in the network layer.
            findBestSequence - If true, the solver should re-sequence the route in
                               the optimal order. The default is as defined in the
                               network layer.
            preserveFirstStop - If true, the solver should keep the first stop
                                fixed in the sequence. The default is as defined
                                in the network layer.
            preserveLastStop - If true, the solver should keep the last stop fixed
                               in the sequence. The default is as defined in the
                               network layer.
            useTimeWindows - If true, the solver should consider time windows.
                             The default is as defined in the network layer.
            startTime - The time the route begins. If not specified, the solver
                        will use the default as defined in the network layer.
            startTimeIsUTC - The time zone of the startTime parameter.
            accumulateAttributeNames - The list of network attribute names to be
                                       accumulated with the analysis. The default is
                                       as defined in the network layer. The value
                                       should be specified as a comma separated list
                                       of attribute names. You can also specify a
                                       value of none to indicate that no network
                                       attributes should be accumulated.
            impedanceAttributeName - The network attribute name to be used as the
                                     impedance attribute in analysis. The default is
                                     as defined in the network layer.
            restrictionAttributeNames -The list of network attribute names to be
                                       used as restrictions with the analysis. The
                                       default is as defined in the network layer.
                                       The value should be specified as a comma
                                       separated list of attribute names. You can
                                       also specify a value of none to indicate that
                                       no network attributes should be used as
                                       restrictions.
            restrictUTurns -  Specifies how U-Turns should be restricted in the
                              analysis. The default is as defined in the network
                              layer. Values: esriNFSBAllowBacktrack |
                              esriNFSBAtDeadEndsOnly | esriNFSBNoBacktrack |
                              esriNFSBAtDeadEndsAndIntersections
            useHierarchy -  If true, the hierarchy attribute for the network should
                            be used in analysis. The default is as defined in the
                            network layer.
            directionsLanguage - The language to be used when computing directions.
                                 The default is as defined in the network layer. The
                                 list of supported languages can be found in REST
                                 layer description.
            directionsOutputType -  Defines content, verbosity of returned
                                    directions. The default is esriDOTStandard.
                                    Values: esriDOTComplete | esriDOTCompleteNoEvents
                                    | esriDOTInstructionsOnly | esriDOTStandard |
                                    esriDOTSummaryOnly
            directionsStyleName - The style to be used when returning the directions.
                                  The default is as defined in the network layer. The
                                  list of supported styles can be found in REST
                                  layer description.
            directionsLengthUnits - The length units to use when computing directions.
                                    The default is as defined in the network layer.
                                    Values: esriNAUFeet | esriNAUKilometers |
                                    esriNAUMeters | esriNAUMiles |
                                    esriNAUNauticalMiles | esriNAUYards |
                                    esriNAUUnknown
            directionsTimeAttributeName - The name of network attribute to use for
                                          the drive time when computing directions.
                                          The default is as defined in the network
                                          layer.
            outputGeometryPrecision -  The precision of the output geometry after
                                       generalization. If 0, no generalization of
                                       output geometry is performed. The default is
                                       as defined in the network service
                                       configuration.
            outputGeometryPrecisionUnits - The units of the output geometry
                                           precision. The default value is
                                           esriUnknownUnits. Values: esriUnknownUnits
                                           | esriCentimeters | esriDecimalDegrees |
                                           esriDecimeters | esriFeet | esriInches |
                                           esriKilometers | esriMeters | esriMiles |
                                           esriMillimeters | esriNauticalMiles |
                                           esriPoints | esriYards
            returnZ - If true, Z values will be included in the returned routes and
                       compressed geometry if the network dataset is Z-aware.
                       The default is false.
        """

        if not self.properties.layerType == "esriNAServerRouteLayer":
            raise ValueError("The solve operation is supported on a network "
                             "layer of Route type only")

        url = self._url + "/solve"
        params = {
                    "f" : "json",
                    "stops": stops
                 }

        if not barriers is None:
            params['barriers'] = barriers
        if not polylineBarriers is None:
            params['polylineBarriers'] = polylineBarriers
        if not polygonBarriers is None:
            params['polygonBarriers'] = polygonBarriers
        if not travelMode is None:
            params['travelMode'] = travelMode
        if not attributeParameterValues is None:
            params['attributeParameterValues'] = attributeParameterValues
        if not returnDirections is None:
            params['returnDirections'] = returnDirections
        if not returnRoutes is None:
            params['returnRoutes'] = returnRoutes
        if not returnStops is None:
            params['returnStops'] = returnStops
        if not returnBarriers is None:
            params['returnBarriers'] = returnBarriers
        if not returnPolylineBarriers is None:
            params['returnPolylineBarriers'] = returnPolylineBarriers
        if not returnPolygonBarriers is None:
            params['returnPolygonBarriers'] = returnPolygonBarriers
        if not outSR is None:
            params['outSR'] = outSR
        if not ignoreInvalidLocations is None:
            params['ignoreInvalidLocations'] = ignoreInvalidLocations
        if not outputLines is None:
            params['outputLines'] = outputLines
        if not findBestSequence is None:
            params['findBestSequence'] = findBestSequence
        if not preserveFirstStop is None:
            params['preserveFirstStop'] = preserveFirstStop
        if not preserveLastStop is None:
            params['preserveLastStop'] = preserveLastStop
        if not useTimeWindows is None:
            params['useTimeWindows'] = useTimeWindows
        if not startTime is None:
            params['startTime'] = startTime
        if not startTimeIsUTC is None:
            params['startTimeIsUTC'] = startTimeIsUTC
        if not accumulateAttributeNames is None:
            params['accumulateAttributeNames'] = accumulateAttributeNames
        if not impedanceAttributeName is None:
            params['impedanceAttributeName'] = impedanceAttributeName
        if not restrictionAttributeNames is None:
            params['restrictionAttributeNames'] = restrictionAttributeNames
        if not restrictUTurns is None:
            params['restrictUTurns'] = restrictUTurns
        if not useHierarchy is None:
            params['useHierarchy'] = useHierarchy
        if not directionsLanguage is None:
            params['directionsLanguage'] = directionsLanguage
        if not directionsOutputType is None:
            params['directionsOutputType'] = directionsOutputType
        if not directionsStyleName is None:
            params['directionsStyleName'] = directionsStyleName
        if not directionsLengthUnits is None:
            params['directionsLengthUnits'] = directionsLengthUnits
        if not directionsTimeAttributeName is None:
            params['directionsTimeAttributeName'] = directionsTimeAttributeName
        if not outputGeometryPrecision is None:
            params['outputGeometryPrecision'] = outputGeometryPrecision
        if not outputGeometryPrecisionUnits is None:
            params['outputGeometryPrecisionUnits'] = outputGeometryPrecisionUnits
        if not returnZ is None:
            params['returnZ'] = returnZ

        return self._con.post(path=url,
                              postdata=params, token=self._token)


class ServiceAreaLayer(NetworkLayer):
    """
    The Service Area Layer which has common properties of Network
    Layer as well as some attributes unique to Service Area Layer
    only.
    """
    def solve_service_area(self,facilities,
                         barriers=None,
                         polylineBarriers=None,
                         polygonBarriers=None,
                         travelMode=None,
                         attributeParameterValues=None,
                         defaultBreaks=None,
                         excludeSourcesFromPolygons=None,
                         mergeSimilarPolygonRanges=None,
                         outputLines=None,
                         outputPolygons=None,
                         overlapLines=None,
                         overlapPolygons=None,
                         splitLinesAtBreaks=None,
                         splitPolygonsAtBreaks=None,
                         trimOuterPolygon=None,
                         trimPolygonDistance=None,
                         trimPolygonDistanceUnits=None,
                         returnFacilities=False,
                         returnBarriers=False,
                         returnPolylineBarriers=False,
                         returnPolygonBarriers=False,
                         outSR=None,
                         accumulateAttributeNames=None,
                         impedanceAttributeName=None,
                         restrictionAttributeNames=None,
                         restrictUTurns=None,
                         outputGeometryPrecision=None,
                         outputGeometryPrecisionUnits='esriUnknownUnits',
                         useHierarchy=None,
                         timeOfDay=None,
                         timeOfDayIsUTC=None,
                         travelDirection=None,
                         returnZ=False):
        """ The solve service area operation is performed on a network layer
        resource of type service area (layerType is esriNAServerServiceArea).
        You can provide arguments to the solve service area operation as
        query parameters.
        Inputs:
            facilities - The set of facilities loaded as network locations
                         during analysis. Facilities can be specified using
                         a simple comma / semi-colon based syntax or as a
                         JSON structure. If facilities are not specified,
                         preloaded facilities from the map document are used
                         in the analysis. If an empty json object is passed
                         ('{}') preloaded facilities are ignored.
            barriers - The set of barriers loaded as network locations during
                       analysis. Barriers can be specified using a simple
                       comma/semicolon-based syntax or as a JSON structure.
                       If barriers are not specified, preloaded barriers from
                       the map document are used in the analysis. If an empty
                       json object is passed ('{}'), preloaded barriers are
                       ignored.
            polylineBarriers - The set of polyline barriers loaded as network
                               locations during analysis. If polyline barriers
                               are not specified, preloaded polyline barriers
                               from the map document are used in the analysis.
                               If an empty json object is passed ('{}'),
                               preloaded polyline barriers are ignored.
            polygonBarriers - The set of polygon barriers loaded as network
                              locations during analysis. If polygon barriers
                              are not specified, preloaded polygon barriers
                              from the map document are used in the analysis.
                              If an empty json object is passed ('{}'),
                              preloaded polygon barriers are ignored.
            travelMode - Travel modes provide override values that help you
                         quickly and consistently model a vehicle or mode of
                         transportation. The chosen travel mode must be
                         preconfigured on the network dataset that the
                         service area service references.
            attributeParameterValues - A set of attribute parameter values that
                                       can be parameterized to determine which
                                       network elements can be used by a vehicle.
            defaultBreaks - A comma-separated list of doubles. The default is
                            defined in the network analysis layer.
            excludeSourcesFromPolygons - A comma-separated list of string names.
                                         The default is defined in the network
                                         analysis layer.

            mergeSimilarPolygonRanges - If true, similar ranges will be merged
                                        in the result polygons. The default is
                                        defined in the network analysis layer.
            outputLines - The type of lines(s) generated. The default is as
                          defined in the network analysis layer.
            outputPolygons - The type of polygon(s) generated. The default is
                             as defined in the network analysis layer.
            overlapLines - Indicates if the lines should overlap from multiple
                           facilities. The default is defined in the network
                           analysis layer.
            overlapPolygons - Indicates if the polygons for all facilities
                              should overlap. The default is defined in the
                              network analysis layer.
            splitLinesAtBreaks - If true, lines will be split at breaks. The
                                 default is defined in the network analysis
                                 layer.
            splitPolygonsAtBreaks - If true, polygons will be split at breaks.
                                    The default is defined in the network
                                    analysis layer.
            trimOuterPolygon -  If true, the outermost polygon (at the maximum
                                break value) will be trimmed. The default is
                                defined in the network analysis layer.
            trimPolygonDistance -  If polygons are being trimmed, provides the
                                   distance to trim. The default is defined in
                                   the network analysis layer.
            trimPolygonDistanceUnits - If polygons are being trimmed, specifies
                                       the units of the trimPolygonDistance. The
                                       default is defined in the network analysis
                                       layer.
            returnFacilities - If true, facilities will be returned with the
                               analysis results. Default is false.
            returnBarriers - If true, barriers will be returned with the analysis
                             results. Default is false.
            returnPolylineBarriers - If true, polyline barriers will be returned
                                     with the analysis results. Default is false.
            returnPolygonBarriers - If true, polygon barriers will be returned
                                    with the analysis results. Default is false.
            outSR - The well-known ID of the spatial reference for the geometries
                    returned with the analysis results. If outSR is not specified,
                    the geometries are returned in the spatial reference of the map.
            accumulateAttributeNames - The list of network attribute names to be
                                       accumulated with the analysis. The default
                                       is as defined in the network analysis layer.
                                       The value should be specified as a comma
                                       separated list of attribute names. You can
                                       also specify a value of none to indicate that
                                       no network attributes should be accumulated.
            impedanceAttributeName - The network attribute name to be used as the
                                     impedance attribute in analysis. The default
                                     is as defined in the network analysis layer.
            restrictionAttributeNames - The list of network attribute names to be
                                        used as restrictions with the analysis. The
                                        default is as defined in the network analysis
                                        layer. The value should be specified as a
                                        comma separated list of attribute names.
                                        You can also specify a value of none to
                                        indicate that no network attributes should
                                        be used as restrictions.
            restrictUTurns - Specifies how U-Turns should be restricted in the
                             analysis. The default is as defined in the network
                             analysis layer. Values: esriNFSBAllowBacktrack |
                             esriNFSBAtDeadEndsOnly | esriNFSBNoBacktrack |
                             esriNFSBAtDeadEndsAndIntersections
            outputGeometryPrecision - The precision of the output geometry after
                                      generalization. If 0, no generalization of
                                      output geometry is performed. The default is
                                      as defined in the network service configuration.
            outputGeometryPrecisionUnits - The units of the output geometry precision.
                                           The default value is esriUnknownUnits.
                                           Values: esriUnknownUnits | esriCentimeters |
                                           esriDecimalDegrees | esriDecimeters |
                                           esriFeet | esriInches | esriKilometers |
                                           esriMeters | esriMiles | esriMillimeters |
                                           esriNauticalMiles | esriPoints | esriYards
            useHierarchy - If true, the hierarchy attribute for the network should be
                           used in analysis. The default is as defined in the network
                           layer. This cannot be used in conjunction with outputLines.
            timeOfDay - The date and time at the facility. If travelDirection is set
                        to esriNATravelDirectionToFacility, the timeOfDay value
                        specifies the arrival time at the facility. if travelDirection
                        is set to esriNATravelDirectionFromFacility, the timeOfDay
                        value is the departure time from the facility. The time zone
                        for timeOfDay is specified by timeOfDayIsUTC.
            timeOfDayIsUTC - The time zone or zones of the timeOfDay parameter. When
                             set to false, which is the default value, the timeOfDay
                             parameter refers to the time zone or zones in which the
                             facilities are located. Therefore, the start or end times
                             of the service areas are staggered by time zone.
            travelDirection - Options for traveling to or from the facility. The
                              default is defined in the network analysis layer.
            returnZ - If true, Z values will be included in saPolygons and saPolylines
                      geometry if the network dataset is Z-aware.
    """
        if not self.properties.layerType == "esriNAServerServiceAreaLayer":
            raise TypeError("The solveServiceArea operation is supported on a network "
                             "layer of Service Area type only")

        url = self._url + "/solveServiceArea"
        params = {
                "f" : "json",
                "facilities": facilities
                }

        if not barriers is None:
            params['barriers'] = barriers
        if not polylineBarriers is None:
            params['polylineBarriers'] = polylineBarriers
        if not polygonBarriers is None:
            params['polygonBarriers'] = polygonBarriers
        if not travelMode is None:
            params['travelMode'] = travelMode
        if not attributeParameterValues is None:
            params['attributeParameterValues'] = attributeParameterValues
        if not defaultBreaks is None:
            params['defaultBreaks'] = defaultBreaks
        if not excludeSourcesFromPolygons is None:
            params['excludeSourcesFromPolygons'] = excludeSourcesFromPolygons
        if not mergeSimilarPolygonRanges is None:
            params['mergeSimilarPolygonRanges'] = mergeSimilarPolygonRanges
        if not outputLines is None:
            params['outputLines'] = outputLines
        if not outputPolygons is None:
            params['outputPolygons'] = outputPolygons
        if not overlapLines is None:
            params['overlapLines'] = overlapLines
        if not overlapPolygons is None:
            params['overlapPolygons'] = overlapPolygons
        if not splitLinesAtBreaks is None:
            params['splitLinesAtBreaks'] = splitLinesAtBreaks
        if not splitPolygonsAtBreaks is None:
            params['splitPolygonsAtBreaks'] = splitPolygonsAtBreaks
        if not trimOuterPolygon is None:
            params['trimOuterPolygon'] = trimOuterPolygon
        if not trimPolygonDistance is None:
            params['trimPolygonDistance'] = trimPolygonDistance
        if not trimPolygonDistanceUnits is None:
            params['trimPolygonDistanceUnits'] = trimPolygonDistanceUnits
        if not returnFacilities is None:
            params['returnFacilities'] = returnFacilities
        if not returnBarriers is None:
            params['returnBarriers'] = returnBarriers
        if not returnPolylineBarriers is None:
            params['returnPolylineBarriers'] = returnPolylineBarriers
        if not returnPolygonBarriers is None:
            params['returnPolygonBarriers'] = returnPolygonBarriers
        if not outSR is None:
            params['outSR'] = outSR
        if not accumulateAttributeNames is None:
            params['accumulateAttributeNames'] = accumulateAttributeNames
        if not impedanceAttributeName is None:
            params['impedanceAttributeName'] = impedanceAttributeName
        if not restrictionAttributeNames is None:
            params['restrictionAttributeNames'] = restrictionAttributeNames
        if not restrictUTurns is None:
            params['restrictUTurns'] = restrictUTurns
        if not outputGeometryPrecision is None:
            params['outputGeometryPrecision'] = outputGeometryPrecision
        if not outputGeometryPrecisionUnits is None:
            params['outputGeometryPrecisionUnits'] = outputGeometryPrecisionUnits
        if not useHierarchy is None:
            params['useHierarchy'] = useHierarchy
        if not timeOfDay is None:
            params['timeOfDay'] = timeOfDay
        if not timeOfDayIsUTC is None:
            params['timeOfDayIsUTC'] = timeOfDayIsUTC
        if not travelDirection is None:
            params['travelDirection'] = travelDirection
        if not returnZ is None:
            params['returnZ'] = returnZ

        return self._con.post(path=url,
                              postdata=params, token=self._token)


class ClosestFacilityLayer(NetworkLayer):
    """
    The Closest Facility Network Layer which has common properties of Network
    Layer as well as some attributes unique to Closest Facility Layer
    only.
    """
    def solve_closest_facility(self,incidents,facilities,
                             barriers=None,
                             polylineBarriers=None,
                             polygonBarriers=None,
                             travelMode=None,
                             attributeParameterValues=None,
                             returnDirections=None,
                             directionsLanguage=None,
                             directionsStyleName=None,
                             directionsLengthUnits=None,
                             directionsTimeAttributeName=None,
                             returnCFRoutes=True,
                             returnFacilities=False,
                             returnIncidents=False,
                             returnBarriers=False,
                             returnPolylineBarriers=False,
                             returnPolygonBarriers=False,
                             outputLines=None,
                             defaultCutoff=None,
                             defaultTargetFacilityCount=None,
                             travelDirection=None,
                             outSR=None,
                             accumulateAttributeNames=None,
                             impedanceAttributeName=None,
                             restrictionAttributeNames=None,
                             restrictUTurns=None,
                             useHierarchy=True,
                             outputGeometryPrecision=None,
                             outputGeometryPrecisionUnits=None,
                             timeOfDay=None,
                             timeOfDayIsUTC=None,
                             timeOfDayUsage=None,
                             returnZ=False):
        """The solve operation is performed on a network layer resource of
        type closest facility (layerType is esriNAServerClosestFacilityLayer).
        You can provide arguments to the solve route operation as query
        parameters.
        Inputs:
            facilities  - The set of facilities loaded as network locations
                          during analysis. Facilities can be specified using
                          a simple comma / semi-colon based syntax or as a
                          JSON structure. If facilities are not specified,
                          preloaded facilities from the map document are used
                          in the analysis.
            incidents - The set of incidents loaded as network locations
                        during analysis. Incidents can be specified using
                        a simple comma / semi-colon based syntax or as a
                        JSON structure. If incidents are not specified,
                        preloaded incidents from the map document are used
                        in the analysis.
            barriers - The set of barriers loaded as network locations during
                       analysis. Barriers can be specified using a simple comma
                       / semi-colon based syntax or as a JSON structure. If
                       barriers are not specified, preloaded barriers from the
                       map document are used in the analysis. If an empty json
                       object is passed ('{}') preloaded barriers are ignored.
            polylineBarriers - The set of polyline barriers loaded as network
                               locations during analysis. If polyline barriers
                               are not specified, preloaded polyline barriers
                               from the map document are used in the analysis.
                               If an empty json object is passed ('{}')
                               preloaded polyline barriers are ignored.
            polygonBarriers - The set of polygon barriers loaded as network
                              locations during analysis. If polygon barriers
                              are not specified, preloaded polygon barriers
                              from the map document are used in the analysis.
                              If an empty json object is passed ('{}') preloaded
                              polygon barriers are ignored.
            travelMode - Travel modes provide override values that help you
                         quickly and consistently model a vehicle or mode of
                         transportation. The chosen travel mode must be
                         preconfigured on the network dataset that the routing
                         service references.
            attributeParameterValues - A set of attribute parameter values that
                                       can be parameterized to determine which
                                       network elements can be used by a vehicle.
            returnDirections - If true, directions will be generated and returned
                               with the analysis results. Default is true.
            directionsLanguage - The language to be used when computing directions.
                                 The default is as defined in the network layer. The
                                 list of supported languages can be found in REST
                                 layer description.
            directionsOutputType -  Defines content, verbosity of returned
                                    directions. The default is esriDOTStandard.
                                    Values: esriDOTComplete | esriDOTCompleteNoEvents
                                    | esriDOTInstructionsOnly | esriDOTStandard |
                                    esriDOTSummaryOnly
            directionsStyleName - The style to be used when returning the directions.
                                  The default is as defined in the network layer. The
                                  list of supported styles can be found in REST
                                  layer description.
            directionsLengthUnits - The length units to use when computing directions.
                                    The default is as defined in the network layer.
                                    Values: esriNAUFeet | esriNAUKilometers |
                                    esriNAUMeters | esriNAUMiles |
                                    esriNAUNauticalMiles | esriNAUYards |
                                    esriNAUUnknown
            directionsTimeAttributeName - The name of network attribute to use for
                                          the drive time when computing directions.
                                          The default is as defined in the network
                                          layer.
            returnCFRoutes - If true, closest facilities routes will be returned
                             with the analysis results. Default is true.
            returnFacilities -  If true, facilities  will be returned with the
                                analysis results. Default is false.
            returnIncidents - If true, incidents will be returned with the
                              analysis results. Default is false.
            returnBarriers -  If true, barriers will be returned with the analysis
                              results. Default is false.
            returnPolylineBarriers -  If true, polyline barriers will be returned
                                      with the analysis results. Default is false.
            returnPolygonBarriers - If true, polygon barriers will be returned with
                                    the analysis results. Default is false.
            outputLines - The type of output lines to be generated in the result.
                          The default is as defined in the network layer.
            defaultCutoff - The default cutoff value to stop traversing.
            defaultTargetFacilityCount - The default number of facilities to find.
            travelDirection - Options for traveling to or from the facility.
                              The default is defined in the network layer.
                              Values: esriNATravelDirectionFromFacility |
                              esriNATravelDirectionToFacility
            outSR - The spatial reference of the geometries returned with the
                    analysis results.
            accumulateAttributeNames - The list of network attribute names to be
                                       accumulated with the analysis. The default is
                                       as defined in the network layer. The value
                                       should be specified as a comma separated list
                                       of attribute names. You can also specify a
                                       value of none to indicate that no network
                                       attributes should be accumulated.
            impedanceAttributeName - The network attribute name to be used as the
                                     impedance attribute in analysis. The default is
                                     as defined in the network layer.
            restrictionAttributeNames -The list of network attribute names to be
                                       used as restrictions with the analysis. The
                                       default is as defined in the network layer.
                                       The value should be specified as a comma
                                       separated list of attribute names. You can
                                       also specify a value of none to indicate that
                                       no network attributes should be used as
                                       restrictions.
            restrictUTurns -  Specifies how U-Turns should be restricted in the
                              analysis. The default is as defined in the network
                              layer. Values: esriNFSBAllowBacktrack |
                              esriNFSBAtDeadEndsOnly | esriNFSBNoBacktrack |
                              esriNFSBAtDeadEndsAndIntersections
            useHierarchy -  If true, the hierarchy attribute for the network should
                            be used in analysis. The default is as defined in the
                            network layer.
            outputGeometryPrecision -  The precision of the output geometry after
                                       generalization. If 0, no generalization of
                                       output geometry is performed. The default is
                                       as defined in the network service
                                       configuration.
            outputGeometryPrecisionUnits - The units of the output geometry
                                           precision. The default value is
                                           esriUnknownUnits. Values: esriUnknownUnits
                                           | esriCentimeters | esriDecimalDegrees |
                                           esriDecimeters | esriFeet | esriInches |
                                           esriKilometers | esriMeters | esriMiles |
                                           esriMillimeters | esriNauticalMiles |
                                           esriPoints | esriYards
            timeOfDay - Arrival or departure date and time. Values: specified by
                        number of milliseconds since midnight Jan 1st, 1970, UTC.
            timeOfDayIsUTC - The time zone of the timeOfDay parameter. By setting
                             timeOfDayIsUTC to true, the timeOfDay parameter refers
                             to Coordinated Universal Time (UTC). Choose this option
                             if you want to find what's nearest for a specific time,
                             such as now, but aren't certain in which time zone the
                             facilities or incidents will be located.
            timeOfDayUsage - Defines the way timeOfDay value is used. The default
                             is as defined in the network layer.
                             Values: esriNATimeOfDayUseAsStartTime |
                             esriNATimeOfDayUseAsEndTime
            returnZ - If true, Z values will be included in the returned routes and
                       compressed geometry if the network dataset is Z-aware.
                       The default is false.
    """

        if not self.properties.layerType == "esriNAServerClosestFacilityLayer":
            raise TypeError("The solveClosestFacility operation is supported on a network "
                             "layer of Closest Facility type only")

        url = self._url + "/solveClosestFacility"
        params = {
                "f" : "json",
                "facilities": facilities,
                "incidents": incidents
                }

        if not barriers is None:
            params['barriers'] = barriers
        if not polylineBarriers is None:
            params['polylineBarriers'] = polylineBarriers
        if not polygonBarriers is None:
            params['polygonBarriers'] = polygonBarriers
        if not travelMode is None:
            params['travelMode'] = travelMode
        if not attributeParameterValues is None:
            params['attributeParameterValues'] = attributeParameterValues
        if not returnDirections is None:
            params['returnDirections'] = returnDirections
        if not directionsLanguage is None:
            params['directionsLanguage'] = directionsLanguage
        if not directionsStyleName is None:
            params['directionsStyleName'] = directionsStyleName
        if not directionsLengthUnits is None:
            params['directionsLengthUnits'] = directionsLengthUnits
        if not directionsTimeAttributeName is None:
            params['directionsTimeAttributeName'] = directionsTimeAttributeName
        if not returnCFRoutes is None:
            params['returnCFRoutes'] = returnCFRoutes
        if not returnFacilities is None:
            params['returnFacilities'] = returnFacilities
        if not returnIncidents is None:
            params['returnIncidents'] = returnIncidents
        if not returnBarriers is None:
            params['returnBarriers'] = returnBarriers
        if not returnPolylineBarriers is None:
            params['returnPolylineBarriers'] = returnPolylineBarriers
        if not returnPolygonBarriers is None:
            params['returnPolygonBarriers'] = returnPolygonBarriers
        if not outputLines is None:
            params['outputLines'] = outputLines
        if not defaultCutoff is None:
            params['defaultCutoff'] = defaultCutoff
        if not defaultTargetFacilityCount is None:
            params['defaultTargetFacilityCount'] = defaultTargetFacilityCount
        if not travelDirection is None:
            params['travelDirection'] = travelDirection
        if not outSR is None:
            params['outSR'] = outSR
        if not accumulateAttributeNames is None:
            params['accumulateAttributeNames'] = accumulateAttributeNames
        if not impedanceAttributeName is None:
            params['impedanceAttributeName'] = impedanceAttributeName
        if not restrictionAttributeNames is None:
            params['restrictionAttributeNames'] = restrictionAttributeNames
        if not restrictUTurns is None:
            params['restrictUTurns'] = restrictUTurns
        if not useHierarchy is None:
            params['useHierarchy'] = useHierarchy
        if not outputGeometryPrecision is None:
            params['outputGeometryPrecision'] = outputGeometryPrecision
        if not outputGeometryPrecisionUnits is None:
            params['outputGeometryPrecisionUnits'] = outputGeometryPrecisionUnits
        if not timeOfDay is None:
            params['timeOfDay'] = timeOfDay
        if not timeOfDayIsUTC is None:
            params['timeOfDayIsUTC'] = timeOfDayIsUTC
        if not timeOfDayUsage is None:
            params['timeOfDayUsage'] = timeOfDayUsage
        if not returnZ is None:
            params['returnZ'] = returnZ

        return self._con.post(path=url, postdata=params, token=self._token)


class NetworkDataset(_GISResource):
    """
    A network dataset containing a collection of network layers including route layers,
    service area layers and closest facility layers.
    """
    def __init__(self, url, gis=None):
        super(NetworkDataset, self).__init__(url, gis)
        self._load_layers()

    @classmethod
    def fromitem(cls, item):
        """Creates a network dataset from a 'Network Analysis Service' Item in the GIS"""
        if not item.type == 'Network Analysis Service':
            raise TypeError("item must be a type of Network Analysis Service, not " + item.type)

        return cls(item.url, item._gis)

    #----------------------------------------------------------------------
    def _load_layers(self):
        """loads the various layer types"""
        self._closestFacilityLayers = []
        self._routeLayers = []
        self._serviceAreaLayers = []
        params = {
            "f" : "json",
        }
        json_dict = self._con.get(path=self._url, params=params, token=self._token)
        for k,v in json_dict.items():
            if k == "routeLayers" and json_dict[k]:
                self._routeLayers = []
                for rl in v:
                    self._routeLayers.append(
                        RouteLayer(url=self._url + "/%s" % rl,
                                   gis=self._gis))
            elif k == "serviceAreaLayers" and json_dict[k]:
                self._serviceAreaLayers = []
                for sal in v:
                    self._serviceAreaLayers.append(
                        ServiceAreaLayer(url=self._url + "/%s" % sal,
                                         gis=self._gis))
            elif k == "closestFacilityLayers" and json_dict[k]:
                self._closestFacilityLayers = []
                for cf in v:
                    self._closestFacilityLayers.append(
                        ClosestFacilityLayer(url=self._url + "/%s" % cf,
                                             gis=self._gis))
    #----------------------------------------------------------------------
    @property
    def route_layers(self):
        """List of route layers in this network dataset"""
        if self._routeLayers is None:
            self._load_layers()
        return self._routeLayers
    #----------------------------------------------------------------------
    @property
    def service_area_layers(self):
        """List of service area layers in this network dataset"""
        if self._serviceAreaLayers is None:
            self._load_layers()
        return self._serviceAreaLayers
    #----------------------------------------------------------------------
    @property
    def closest_facility_layers(self):
        """List of closest facility layers in this network dataset"""
        if self._closestFacilityLayers is None:
            self._load_layers()
        return self._closestFacilityLayers
