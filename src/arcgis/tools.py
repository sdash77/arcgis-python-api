"""
The arcgis.tools module is used for consuming the GIS functionality exposed from ArcGIS Online 
or Portal web services. It has implementations for Spatial Analysis tools, GeoAnalytics tools,
Raster Analysis tools, Geoprocessing tools, Geocoders and Geometry Utility services. 
These tools primarily operate on items and layers from the GIS. 
"""
import re
import sys
import json
import types
import json
from pandas.io.json import json_normalize
from contextlib import contextmanager
from arcgis.lyr import *

import urllib.parse
import inspect
import datetime
import collections
import arcgis.gis
import time

import tempfile
import os
import string
import random

def _id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@contextmanager
def _tempinput(data):
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write((bytes(data, 'UTF-8')))
    temp.close()
    yield temp.name
    os.unlink(temp.name)

def _get_hosted_server_admin_url(servers):
    for server in servers:
        if server['isHosted']: 
            return server['adminUrl'] + '/admin'
    return None

class Geocoder(collections.OrderedDict):
    """Geocoder represents a geocode service resource exposed by the GIS. 
    It can find point locations of addresses, business names, and so on. 
    The output points can be visualized on a map, inserted as stops for a route,
    or loaded as input for spatial analysis. It is also used to generate 
    batch results for a set of addresses, as well as for reverse geocoding,
    i.e. determining the address at a particular x/y location. 
    
    An instance of the Geocoder is available through the gis.tools.geocoder 
    property, accessible from the GIS object.
    """
    def __init__(self, item, url=None, gis=None):
        """
        Constructs a Geocoder object given a geocoding service item from ArcGIS Online or Portal.
        """
        if url is not None:
            self.url = url
            self._portal = gis._portal
        else:
            if item.type.lower() != 'geocoding service':
                raise TypeError("item type must be geocoding service")
            self._portal = item._portal
            self.url = item.url
        
        params = {
            "f" : "json"
        }
        #print(self.url)
        svcprops = self._portal.con.post(self.url, params, use_ordered_dict=True)
        collections.OrderedDict.__init__(self, svcprops)
        try:
            self._address_field = svcprops['singleLineAddressField']['name']
        except:
            print("Geocoder does not support single line address input")

    def __str__(self):
        # return "Geocode service at " + self.url
        return json.dumps(self)

    def geocode(self,
             address,
             searchExtent=None,
             location=None,
             distance=None,
             outSR=None,
             category=None,
             outFields="*",
             maxLocations=20,
             magicKey=None,
             forStorage=False):
        """
        The geocode method geocodes one location per request.

        Inputs:
           address - Specifies the location to be geocoded. This can be a string 
           containing the street address, place name, postal code, or POI. 
            
            Alternatively, this can be a dictionary containing the various address fields accepted by the corresponding geocode service. These fields are listed in the addressFields property of the associated geocode service resource. For example, if the addressFields of a geocode service resource includes fields with the following names: Street, City, State and Zone, then the address argument is of the form:
            {
              Street: "1234 W Main St",
              City: "Small Town",
              State: "WA",
              Zone: "99027"
            }
           
           searchExtent - A set of bounding box coordinates that limit the search
            area to a specific region. This is especially useful for
            applications in which a user will search for places and
            addresses only within the current map extent.
           location - Defines an origin point location that is used with
            the distance parameter to sort geocoding candidates based upon
            their proximity to the location. The distance parameter
            specifies the radial distance from the location in meters. The
            priority of candidates within this radius is boosted relative
            to those outside the radius.
           distance - Specifies the radius of an area around a point
            location which is used to boost the rank of geocoding
            candidates so that candidates closest to the location are
            returned first. The distance value is in meters.
           outSR - The spatial reference of the x/y coordinates returned by
            a geocode request. This is useful for applications using a map
            with a spatial reference different than that of the geocode
            service.
           category - A place or address type which can be used to filter
            find results. The parameter supports input of single category
            values or multiple comma-separated values. The category
            parameter can be passed in a request with or without the text
            parameter.
           outFields - The list of fields to be returned in the response.
           maxLocation - The maximum number of locations to be returned by
            a search, up to the maximum number allowed by the service. If
            not specified, then one location will be returned.
            
           magicKey - The find operation retrieves results quicker when you
            pass in valid text and magicKey values than when you don't pass
            in magicKey. However, to get these advantages, you need to make
            a prior request to suggest, which provides a magicKey. This may
            or may not be relevant to your workflow.

           forStorage - Specifies whether the results of the operation will
            be persisted. The default value is false, which indicates the
            results of the operation can't be stored, but they can be
            temporarily displayed on a map for instance. If you store the
            results, in a database for example, you need to set this
            parameter to true.
        """
        #self.url + 
        url = self.url + "/findAddressCandidates"

        params = {
            "f" : "json",
        }
        
        if address is not None:
            if isinstance(address, str):
                params[self._address_field] = address
            elif isinstance(address, dict):
                params.update(address)
            else:
                print("address should be a string (single line address) or dictionary (with address fields as keys)")

        #params['text'] = text

        if not magicKey is None:
            params['magicKey'] = magicKey
        if not searchExtent is None:
            params['searchExtent'] = searchExtent
        if not location is None and \
                isinstance(location, list):
            params['location'] = "%s,%s" % (location[0], location[1])
        elif location is not None:
            params['location'] = location
        if not distance is None:
            params['distance'] = distance
        if not outSR is None:
            params['outSR'] = outSR
        if not category is None:
            params['category'] = category
        if outFields is None:
            params['outFields'] = "*"
        else:
            params['outFields'] = outFields
        if not maxLocations is None:
            params['maxLocations'] = maxLocations
        if not forStorage is None:
            params['forStorage'] = forStorage

        resp = self._portal.con.post(url, params)
        if resp is not None:
            return resp['candidates']
        else:
            return []

    def reverse_geocode(self, location, distance=None, outSR=None, langCode=None, returnIntersection=False, forStorage=False):
        """
        The reverseGeocode operation determines the address at a particular
        x/y location. You pass the coordinates of a point location to the
        geocoding service, and the service returns the address that is
        closest to the location.
        Input:
           location - a list defined as [X,Y] or a JSON Point 
        """
        params = {
            "f" : "json"
        }
        url = self.url + "/reverseGeocode"
        if isinstance(location, list):
            params['location'] = "%s,%s" % (location[0], location[1])
        elif isinstance(location, dict):
            params['location'] = location
        else:
            raise Exception("Invalid location")
        
        if distance is not None:
            params['distance'] = distance
        if outSR is not None:
            params['outSR'] = outSR
        if langCode is not None:
            params['langCode'] = langCode
        if returnIntersection:
            params['returnIntersection'] = returnIntersection
        if forStorage:
            params['forStorage'] = forStorage

        resp = self._portal.con.post(url, params)
        return resp
    
    def batch_geocode(self,
                         addresses,
                         sourceCountry=None,
                         category=None,
                         outSR=None):
        """
        The batch_geocode() method geocodes an entire list of addresses. Geocoding many addresses at once is also known as bulk geocoding.
        

        Inputs:
           addresses - A list of addresses to be geocoded.
           For passing in the location name as a single line of text —
           single field batch geocoding — use a string.
           For passing in the location name as multiple lines of text 
           multifield batch geocoding — use the address fields described 
           in the Geocoder documentation.
            The maximum number of addresses that can be geocoded in a
            single request is limited to the SuggestedBatchSize property of
            the locator.
            Syntax:
             addresses = ["380 New York St, Redlands, CA", 
             "1 World Way, Los Angeles, CA",
             "1200 Getty Center Drive, Los Angeles, CA", 
             "5905 Wilshire Boulevard, Los Angeles, CA",
             "100 Universal City Plaza, Universal City, CA 91608",
             "4800 Oak Grove Dr, Pasadena, CA 91109"]

             OR

             addresses= [{
                "Address": "380 New York St.",
                "City": "Redlands",
                "Region": "CA",
                "Postal": "92373"
            },{
                "Address": "1 World Way",
                "City": "Los Angeles",
                "Region": "CA",
                "Postal": "90045"
            }]

           sourceCountry - The sourceCountry parameter is only supported by
            geocode services published using StreetMap Premium locators.
            Added at 10.3 and only supported by geocode services published
            with ArcGIS 10.3 for Server and later versions.
           category - The category parameter is only supported by geocode
            services published using StreetMap Premium locators.
           outSR - The well-known ID of the spatial reference, or a spatial
            reference json object for the returned addresses. For a list of
            valid WKID values, see Projected coordinate systems and
            Geographic coordinate systems.
        """
        params = {
            "f" : "json"
        }
        url = self.url + "/geocodeAddresses"
        if outSR is not None:
            params['outSR'] = outSR
        if sourceCountry is not None:
            params['sourceCountry'] = sourceCountry
        if category is not None:
            params['category'] = category



        addr_recordset = []
        n = len(addresses)

        for index in range(len(addresses)):
            address = addresses[index]

            attributes = { "OBJECTID" : index }
            if isinstance(address, str):
                attributes[self._address_field] = address
            elif isinstance(address, dict):
                attributes.update(address)
            else:
                print("Unsupported address: " + str(address))
                print("address should be a string (single line address) or dictionary (with address fields as keys)")

            addr_rec = { "attributes" : attributes }
            addr_recordset.append(addr_rec)

        params['addresses'] = { "records" : addr_recordset }
        
        resp = self._portal.con.post(url, params)
        if resp is not None:
            return resp['locations']
        else:
            return []
    
    def find_best_match(self,
             address,
             searchExtent=None,
             location=None,
             distance=None,
             outSR=None,
             category=None,
             outFields="*",magicKey=None,
             forStorage=False):
        """Returns the (latitude, longitude) or (y, x) coordinates of the best match for specified address"""
        location = self.geocode(address,  sourceCountry, searchExtent, location, distance, 
                         outSR, category, outFields, 1, magicKey,
                         forStorage)[0]['location']
        return location['y'], location['x']

    def suggest(self,
                text,
                location,
                distance=None,
                category=None
                ):
        """
        The suggest operation is performed on a geocode service resource.
        The result of this operation is a resource representing a list of
        suggested matches for the input text. This resource provides the
        matching text as well as a unique ID value, which links a
        suggestion to a specific place or address.
        A geocode service must meet the following requirements to support
        the suggest operation:
          The address locator from which the geocode service was published
          must support suggestions. Only address locators created using
          ArcGIS 10.3 for Desktop and later can support suggestions. See
          the Create Address Locator geoprocessing tool help topic for more
          information.
          The geocode service must have the Suggest capability enabled.
          Only geocode services published using ArcGIS 10.3 for Server or
          later support the Suggest capability.
        The suggest operation allows character-by-character auto-complete
        suggestions to be generated for user input in a client application.
        This capability facilitates the interactive search user experience
        by reducing the number of characters that need to be typed before
        a suggested match is obtained. A client application can provide a
        list of suggestions that is updated with each character typed by a
        user until the address they are looking for appears in the list.
        Inputs:
           text - The input text provided by a user that is used by the
            suggest operation to generate a list of possible matches. This
            is a required parameter.
           location -  Defines an origin point location that is used with
            the distance parameter to sort suggested candidates based on
            their proximity to the location. The distance parameter
            specifies the radial distance from the location in meters. The
            priority of candidates within this radius is boosted relative
            to those outside the radius.
            This is useful in mobile applications where a user wants to
            search for places in the vicinity of their current GPS
            location. It is also useful for web mapping applications where
            a user wants to find places within or near the map extent.
            The location parameter can be specified without specifying a
            distance. If distance is not specified, it defaults to 2000
            meters.
            The object can be an common.geometry.Point or X/Y list object
           distance - Specifies the radius around the point defined in the
            location parameter to create an area, which is used to boost
            the rank of suggested candidates so that candidates closest to
            the location are returned first. The distance value is in
            meters.
            If the distance parameter is specified, the location parameter
            must be specified as well.
            It is important to note that the location and distance
            parameters allow searches to extend beyond the specified search
            radius. They are not used to filter results, but rather to rank
            resulting candidates based on their distance from a location.
           category - The category parameter is only supported by geocode
            services published using StreetMap Premium locators.
        """
        params = {
            "f" : "json",
            "text" : text
        }
        url = self.url + "/suggest"
        
        if isinstance(location, list):
            params['location'] = "%s,%s" % (location[0], location[1])
        else:
            raise Exception("Invalid location, please try again")
        if not category is None:
            params['category'] = category
        if not distance is None and \
           isinstance(distance, (int, float)):
            params['distance'] = distance
        resp = self._portal.con.post(url, params)
        return resp
    

class Geometry(collections.OrderedDict):
    "represents a geometry service"
    def __init__(self, item, url=None, gis=None):
        """
        Constructs a Geometry Server object given it's item from ArcGIS Online or Portal.
        """
        if url is not None:
            self.url = url
            self._portal = gis._portal
        else:
            if item.type.lower() != 'geometry service':
                raise TypeError("item type must be geometry service")
            self._portal = item._portal
            self.url = item.url
        
        params = {
            "f" : "json"
        }
        svcprops = self._portal.con.post(self.url, params, use_ordered_dict=True)
        collections.OrderedDict.__init__(self, svcprops)

    def __str__(self):
        return json.dumps(self)

    def areasAndLengths(self,
                        polygons,
                        lengthUnit,
                        areaUnit,
                        calculationType,
                        ):
        """
           The areasAndLengths operation calculates areas and perimeter lengths
           for each polygon specified in the input array.

           Inputs:
              polygons - The array of polygons whose areas and lengths are
                         to be computed.
              lengthUnit - The length unit in which the perimeters of
                           polygons will be calculated. If calculationType
                           is planar, then lengthUnit can be any esriUnits
                           constant. If lengthUnit is not specified, the
                           units are derived from sr. If calculationType is
                           not planar, then lengthUnit must be a linear
                           esriUnits constant, such as esriSRUnit_Meter or
                           esriSRUnit_SurveyMile. If lengthUnit is not
                           specified, the units are meters. For a list of
                           valid units, see esriSRUnitType Constants and
                           esriSRUnit2Type Constant.
              areaUnit - The area unit in which areas of polygons will be
                         calculated. If calculationType is planar, then
                         areaUnit can be any esriUnits constant. If
                         areaUnit is not specified, the units are derived
                         from sr. If calculationType is not planar, then
                         areaUnit must be a linear esriUnits constant such
                         as esriSRUnit_Meter or esriSRUnit_SurveyMile. If
                         areaUnit is not specified, then the units are
                         meters. For a list of valid units, see
                         esriSRUnitType Constants and esriSRUnit2Type
                         constant.
                         The list of valid esriAreaUnits constants include,
                         esriSquareInches | esriSquareFeet |
                         esriSquareYards | esriAcres | esriSquareMiles |
                         esriSquareMillimeters | esriSquareCentimeters |
                         esriSquareDecimeters | esriSquareMeters | esriAres
                         | esriHectares | esriSquareKilometers.
              calculationType -  The type defined for the area and length
                                 calculation of the input geometries. The
                                 type can be one of the following values:
                                 planar - Planar measurements use 2D
                                          Euclidean distance to calculate
                                          area and length. This should
                                          only be used if the area or
                                          length needs to be calculated in
                                          the given spatial reference.
                                          Otherwise, use preserveShape.
                                 geodesic - Use this type if you want to
                                          calculate an area or length using
                                          only the vertices of the polygon
                                          and define the lines between the
                                          points as geodesic segments
                                          independent of the actual shape
                                          of the polygon. A geodesic
                                          segment is the shortest path
                                          between two points on an ellipsoid.
                                 preserveShape - This type calculates the
                                          area or length of the geometry on
                                          the surface of the Earth
                                          ellipsoid. The shape of the
                                          geometry in its coordinate system
                                          is preserved.
           Output:
              JSON as dictionary
        """
        url = self.url + "/areasAndLengths"
        params = {
            "f" : "json",
            "lengthUnit" : lengthUnit,
            "areaUnit" : {"areaUnit" : areaUnit},
            "calculationType" : calculationType
        }

        if isinstance(polygons, list) and len(polygons) > 0:
            p = polygons[0]
            if isinstance(p, Polygon):
                params['sr'] = p.spatialReference['wkid']
                params['polygons'] = [poly.asDictionary for poly in polygons]
            del p
        else:
            return "No polygons provided, please submit a list of polygon geometries"
        
        resp = self._portal.con.post(url, params)
        
        return resp

    def simplify(self,
                 sr,
                 geometries
                 ):
        """returns a simplied geometry object"""
        url = self.url + "/simplify"
        params = {
            "f" : "json",
            "sr" : sr,
            "geometries" : geometries
        }
        resp = self._portal.con.post(url, params)
        
        return resp
    
    def lengths(self,
                sr,
                polylines,
                lengthUnit,
                calculationType
                ):
        """"""
        allowedCalcTypes = ['planar', 'geodesic', 'preserveShape']
        if calculationType not in allowedCalcTypes:
            raise AttributeError("Invalid calculation Type")
        url = self.url + "/lengths"
        params = {
            "f" : "json",
            "sr" : sr,
            "polylines": polylines,
            "lengthUnit" : lengthUnit,
            "calculationType" : calculationType
        }
        resp = self._portal.con.post(url, params)
        
        return resp['lengths']

class _AsyncService(object):

    def __init__(self, url, gis):
        if url is not None:
            self.url = url
            self._portal = gis._portal

    def _analysis_job(self, task, params):
        """ Submits an Analysis job and returns the job URL for monitoring the job
            status in addition to the json response data for the submitted job."""
    
        # Unpack the Analysis job parameters as a dictionary and add token and
        # formatting parameters to the dictionary. The dictionary is used in the
        # HTTP POST request. Headers are also added as a dictionary to be included
        # with the POST.
        #
        #print("Submitting analysis job...")
        
        task_url = "{}/{}".format(self.url, task)
        submit_url = "{}/submitJob".format(task_url)
        
        params["f"] = "json"

        resp = self._portal.con.post(submit_url, params)
        #print(resp)
        return task_url, resp

    def _analysis_job_status(self, task_url, job_info):
        """ Tracks the status of the submitted Analysis job."""

        if "jobId" in job_info:
            # Get the id of the Analysis job to track the status.
            #
            job_id = job_info.get("jobId")
            job_url = "{}/jobs/{}".format(task_url, job_id)
            params = { "f" : "json" }
            job_response = self._portal.con.post(job_url, params)

            # Query and report the Analysis job status.
            #
            num_messages = 0

            if "jobStatus" in job_response:
                while not job_response.get("jobStatus") == "esriJobSucceeded":
                    time.sleep(5)
            
                    job_response = self._portal.con.post(job_url, params)
                    #print(job_response)
                    messages = job_response['messages'] if 'messages' in job_response else []
                    num = len(messages)
                    if num > num_messages:
                        for index in range(num_messages, num):
                            msg = messages[index]
                            if msg['type'] == 'esriJobMessageTypeInformative':
                                print(msg['description'])
                            else:
                                print(msg['description'],file = sys.stderr)
                        num_messages = num

                    if job_response.get("jobStatus") == "esriJobFailed":
                        raise Exception("Job failed.")
                    elif job_response.get("jobStatus") == "esriJobCancelled":
                        raise Exception("Job cancelled.")
                    elif job_response.get("jobStatus") == "esriJobTimedOut":
                        raise Exception("Job timed out.")
                
                if "results" in job_response:
                    return job_response
            else:
                raise Exception("No job results.")
        else:
            raise Exception("No job url.")

    def _analysis_job_results(self, task_url, job_info):
        """ Use the job result json to get information about the feature service
            created from the Analysis job."""

        # Get the paramUrl to get information about the Analysis job results.
        #
        if "jobId" in job_info:
            job_id = job_info.get("jobId")
            if "results" in job_info:
                results = job_info.get("results")
                result_values = {}
                for key in list(results.keys()):
                    param_value = results[key]
                    if "paramUrl" in param_value:
                        param_url = param_value.get("paramUrl")
                        result_url = "{}/jobs/{}/{}".format(task_url, 
                                                                            job_id, 
                                                                            param_url)

                        params = { "f" : "json" }
                        param_result = self._portal.con.post(result_url, params)

                        job_value = param_result.get("value")
                        result_values[key] = job_value
                return result_values
            else:
                raise Exception("Unable to get analysis job results.")
        else:
            raise Exception("Unable to get analysis job results.")

    def _feature_input(self, input_layer):

        point_fs = {  
           "layerDefinition":{  
              "currentVersion":10.11,
              "copyrightText":"",
              "defaultVisibility":True,
              "relationships":[  

              ],
              "isDataVersioned":False,
              "supportsRollbackOnFailureParameter":True,
              "supportsStatistics":True,
              "supportsAdvancedQueries":True,
              "geometryType":"esriGeometryPoint",
              "minScale":0,
              "maxScale":0,
              "objectIdField":"OBJECTID",
              "templates":[  

              ],
              "type":"Feature Layer",
              "displayField":"TITLE",
              "visibilityField":"VISIBLE",
              "name":"startDrawPoint",
              "hasAttachments":False,
              "typeIdField":"TYPEID",
              "capabilities":"Query",
              "allowGeometryUpdates":True,
              "htmlPopupType":"",
              "hasM":False,
              "hasZ":False,
              "globalIdField":"",
              "supportedQueryFormats":"JSON",
              "hasStaticData":False,
              "maxRecordCount":-1,
              "indexes":[  

              ],
              "types":[  

              ],
              "fields":[  
                 {  
                    "alias":"OBJECTID",
                    "name":"OBJECTID",
                    "type":"esriFieldTypeOID",
                    "editable":False
                 },
                 {  
                    "alias":"Title",
                    "name":"TITLE",
                    "length":50,
                    "type":"esriFieldTypeString",
                    "editable":True
                 },
                 {  
                    "alias":"Visible",
                    "name":"VISIBLE",
                    "type":"esriFieldTypeInteger",
                    "editable":True
                 },
                 {  
                    "alias":"Description",
                    "name":"DESCRIPTION",
                    "length":1073741822,
                    "type":"esriFieldTypeString",
                    "editable":True
                 },
                 {  
                    "alias":"Type ID",
                    "name":"TYPEID",
                    "type":"esriFieldTypeInteger",
                    "editable":True
                 }
              ]
           },
           "featureSet":{  
              "features":[  
                 {  
                    "geometry":{  
                       "x":80.27032792000051,
                       "y":13.085227147000467,
                       "spatialReference":{  
                          "wkid": 4326,
                          "latestWkid":4326
                       }
                    },
                  "attributes":{  
                       "description":"blayer desc",
                       "title":"blayer",
                       "OBJECTID":0,
                       "VISIBLE":1
                    },
                    "symbol":{  
                       "angle":0,
                       "xoffset":0,
                       "yoffset":8.15625,
                       "type":"esriPMS",
                       "url":"https://cdn.arcgis.com/cdn/7674/js/jsapi/esri/dijit/images/Directions/greenPoint.png",
                       "imageData":"iVBORw0KGgoAAAANSUhEUgAAABUAAAAdCAYAAABFRCf7AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyRpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMC1jMDYxIDY0LjE0MDk0OSwgMjAxMC8xMi8wNy0xMDo1NzowMSAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNS4xIE1hY2ludG9zaCIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDo4OTI1MkU2ODE0QzUxMUUyQURFMUNDNThGMTA3MjkzMSIgeG1wTU06RG9jdW1lbnRJRD0ieG1wLmRpZDo4OTI1MkU2OTE0QzUxMUUyQURFMUNDNThGMTA3MjkzMSI+IDx4bXBNTTpEZXJpdmVkRnJvbSBzdFJlZjppbnN0YW5jZUlEPSJ4bXAuaWlkOjg5MjUyRTY2MTRDNTExRTJBREUxQ0M1OEYxMDcyOTMxIiBzdFJlZjpkb2N1bWVudElEPSJ4bXAuZGlkOjg5MjUyRTY3MTRDNTExRTJBREUxQ0M1OEYxMDcyOTMxIi8+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwveDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+iVNkdQAABJlJREFUeNp0VltvG0UUnpkdr72261CnCQWEIA9FqOKlqooARUKCtAUhoA+VoBVRhfgFXKSKJ97goRL8ARCIclGgL0VUkBBAoBaVoggEQQVSAhFS06SJje3Y3t25cc7srL3YjddHs3N85pvvfOfMyJRs83n8o+P7POI9yQibooTeBa68ISbSRv+hifpCGHX2s6dnfrrRWjroOPzB0T0+zZ0q8uDRSrniF/MB8X2fADhR8IRRRDphh7Q6rbgtOucU0Sdnj59Z2hb00PtHD+Zp/p2x6uitO4o7iLYP8DMafjVE2wXUboALm50W2ahtXO3q8MTX02fnh0Affu/IkSAXnL55dLzMPU6kURZMIZQhFtRk2VBKcpQTIQVZ21hrdUX4zDcnPv2kBzr59mP3BLnChfGx8YrHPKIAELSzMPhQk+ydzpOvIYwywjFeK7K+vt6IlZw8/+y5RZ4gm9eCUrGCmkUyBkCV0Sd5UlBtTLIhRWQE9ixwsVwe6dY3X4WwJ+j9bx7a7/v5i6O7qlxisFZJAvBF7Rjty56CWlmszilj6BNgXd+syTCO7uNK62nuezyUkWWASTPHDtOjbgOHkJTOsbXAyJhIC+rlODdROM211gcQKBJxoh+EKAs4AGqybHVfBvdICNIU/IDHYbcJiS6le4wwbW1B9UDXJcg9QBxtbglh1BlAJzjoUxIGQZFRwtAypgnjtH0spDG9MWVs34xrN5uBLnEoTKQUgDLgZ6hliLunBaIDhy4LYhyotptZlphGyLUhfyspxxj3AIpaVqikdgyzoGn7p0xNj71rNamweCscWC0qoQ8YRm3K2OgpeFoc+j9FSUYKB+4OgxIK4RcZUJ6RsUgqCrShxWzza9035aw/lzYGY5P4xFSMR5vMcFpm87opL4HjXsr76dLhC2xYhgx3I0BfoS7RCp+3K/e8vn+Ke2zWK+cYofQG9yMlw1eK1aAni9oSWil9eOmFhXkPnbXZ1eXqwVsirfQU9Vynm75lymLbxvpSP4yqI4iR5uWlFxdOI56Xbro5t3qhOrW7ZmL1EOFwp7k6pRXuWaZgBmuwJSIl1fNXXvrxjRTLy2ZTm1v9YeTBXedNbCYZZ1U4pdt+NGiomuKKEvKp5ZM/f5z9zctc1vju1b9cv5q/M/icBd4+KNztlnGWKfYjAMqm+K7zZ/PYP6d+X3TrafbmR8N71QcrOPMLd5RGdj838WFup393orNLWRki6vFv197661i40m6AKwYLneG79BzDPNhNYFWwnfguGyKgPl32bwseoTnKekVpS9n49vorWwv1JsSVwAJHCHcW2Agsk3rBBZXBihhcn11biTfDixpPik1bEZyj34EVXXzJrUccWwrbZo5+B6ztRpvO1kLjjO5qW3YccZ5JeTAecQxqqV0Q6hM5KVIrNL5a/77yQPUyLbK9qiMv49zFhW6MMnPE0dwxlQ48ckXDNHJOq0C2xByreHtxhPk1sK4DEI5dut7+QWCZCyj9MXKLWmD/gl1Xtfhd6F2CI86dv+XiIrdOpeeCDd0VyW7KGbLptn9p/mrgNsIxwzKN0QO3IvlPgAEA3AQhIZtaN54AAAAASUVORK5CYII=",
                       "contentType":"image/png",
                       "width":15.75,
                       "height":21.75
                    }
                 }
              ],
              "geometryType":"esriGeometryPoint"
           },
           "nextObjectId":1
        }

        input_layer_url = ""
        if isinstance(input_layer, arcgis.gis.Item):
            if input_layer.type.lower() == 'feature service':
                fs = FeatureService(input_layer)
                input_layer_url =  fs.layers[0].url #["url"]
                input_param =  {"url": input_layer_url }
            elif input_layer.type.lower() == 'feature collection':
                fcdict = input_layer.get_data()
                fc = FeatureCollection(fcdict['layers'][0])
                input_param =  fc
            else:
                raise TypeError("item type must be feature service or feature collection")

        elif isinstance(input_layer, arcgis.tools.FeatureService):
            input_layer_url = input_layer.layers[0].url #["url"]
            input_param =  {"url": input_layer_url }
        elif isinstance(input_layer, Layer):
            input_layer_url = input_layer.url
            input_param =  {"url": input_layer_url }
        elif isinstance(input_layer, tuple): # geocoder location, convert to point featureset
            input_param = point_fs
            input_param["featureSet"]["features"][0]["geometry"]["x"] = input_layer[1]
            input_param["featureSet"]["features"][0]["geometry"]["y"] = input_layer[0]
        elif isinstance(input_layer, dict): # could add support for geometry one day using geometry -> featureset
            input_param =  input_layer
            """
            res = gis.analysis.trace_downstream({"layerDefinition":
                {
                    "geometryType":"esriGeometryPoint",
                    "fields":[{"alias":"OBJECTID","name":"OBJECTID","type":"esriFieldTypeOID","editable":False},
                              {"alias":"Title","name":"TITLE","length":50,"type":"esriFieldTypeString","editable":True},
                              {"alias":"Visible","name":"VISIBLE","type":"esriFieldTypeInteger","editable":True},
                              {"alias":"Description","name":"DESCRIPTION","length":1073741822,"type":"esriFieldTypeString","editable":True},
                              {"alias":"Type ID","name":"TYPEID","type":"esriFieldTypeInteger","editable":True}]
                },
                "featureSet":{
                    "features":[
                        {
                            "geometry":{
                                "x":8913583.679975435,
                                "y":1460497.641278398,
                                "spatialReference":{"wkid":102100,"latestWkid":3857}
                            },
                            "attributes":{"description":"blayer desc","title":"blayer","OBJECTID":0,"VISIBLE":1},
                
                        }
                    ],
                    "geometryType":"esriGeometryPoint"
                },
                "nextObjectId":1
            })
            """
        elif isinstance(input_layer, str):
            input_layer_url = input_layer
            input_param =  {"url": input_layer_url }
        else:
            raise Exception("Invalid format of input layer. url string, feature service Item, feature service instance or dict supported")
        
        return input_param

    def _raster_input(self, input_raster):
        if isinstance(input_raster, arcgis.gis.Item):
            if input_raster.type.lower() == 'image service':
                input_param =  {"itemId": input_raster.itemid }
            else:
                raise TypeError("item type must be image service")
        elif isinstance(input_raster, str):
            input_param =  {"url": input_raster }
        elif isinstance(input_raster, dict):
            input_param =  input_raster
        else:
            raise Exception("Invalid format of input raster. image service Item or image service url, cloud raster uri or shared data path supported")
        
        return input_param

def _call_generator(fnname, spec):
    """Generate GP function based on spec
    """
    varnames, defaults = zip(*spec)
    varnames = ('self', ) + varnames


    def call(self):
        """Method to invoke the Geoprocessing task"""
        #import sys
        kwargs = locals()
        kwargs.pop('self')
        self.__dict__.update(kwargs)
        
        # args, posargs = self.arguments()

        #print("My args: ")
        #for k, v in kwargs.items():
        #    print(k + " => " + str(v))

        return self._execute(kwargs)
    
    code = call.__code__
    new_code = types.CodeType(len(spec) + 1,
                              0,
                              len(spec) + 2,
                              code.co_stacksize,
                              code.co_flags,
                              code.co_code,
                              code.co_consts,
                              code.co_names,
                              varnames,
                              code.co_filename,
                              fnname,
                              code.co_firstlineno,
                              code.co_lnotab,
                              code.co_freevars,
                              code.co_cellvars)
    """    
     * co_name gives the function name 
     * co_argcount is the number of positional arguments (including 
    arguments with default values) 
     * co_nlocals is the number of local variables used by the function 
    (including arguments) 
     * co_varnames is a tuple containing the names of the local 
    variables (starting with the argument names) 
     * co_cellvars is a tuple containing the names of local variables 
    that are referenced by nested functions 
     * co_freevars is a tuple containing the names of free variables 
     * co_code is a string representing the sequence of bytecode 
    instructions 
     * co_consts is a tuple containing the literals used by the bytecode 
     * co_names is a tuple containing the names used by the bytecode 
     * co_filename is the filename from which the code was compiled 
     * co_firstlineno is the first line number of the function 
     * co_lnotab is a string encoding the mapping from byte code offsets 
    to line numbers (for details see the source code of the interpreter) 
     * co_stacksize is the required stack size (including local 
    variables) 
     * co_flags is an integer encoding a number of flags for the 
    interpreter. 
    """




    return types.FunctionType(new_code,
                              {"__builtins__": __builtins__},
                              argdefs=defaults)

# GP Data types: http://resources.arcgis.com/en/help/main/10.1/index.html#//005700000070000000    
class GeoprocessingTool(collections.OrderedDict):
    "represents a geoprocessing service"
    def __init__(self, item):
        """
        Constructs a Geoprocessing Service object given it's item from ArcGIS Online or Portal.
        """
        if item.type.lower() != 'geoprocessing service':
            raise TypeError("item type must be geoprocessing service")
        self.item = item
        self.url = self.item.url
        self._taskurls = {}
        self._method_params = {}

        print("URL: " + self.url)
        params = {
            "f" : "json"
        }
        svcprops = self.item._portal.con.post(self.url, params, use_ordered_dict=True)
        collections.OrderedDict.__init__(self, svcprops)
        for task in svcprops['tasks']:
            print("Task: " + task)
            fnname = self._camelCase_to_underscore(task)

            taskurl = self.url + "/" + task
            
            self._taskurls[fnname] = taskurl + "/execute"

            taskprops = self.item._portal.con.post(taskurl, params)
            execution_type = taskprops['executionType']
            task_params = taskprops['parameters']

            helpstring = taskprops["displayName"] + "\n"
            if 'docstring' in taskprops:
                helpstring = helpstring + ". " + taskprops['docstring'] + "\nParameters:\n"


            spec = []
            name_type = {}
            for param in task_params:
                
                param_name = param['name']
                
                param_type = param['dataType']
                param_dval = param['defaultValue']
                param_drtn = param['direction']
                
                param_rqrd = param['parameterType']
                
                if param_type == 'GPFeatureRecordSetLayer':
                    param_dval = None

                py_param_type_ = param_type
                if param_type == 'GPBoolean':
                    py_param_type_ = bool
                elif param_type == 'GPDouble':
                    py_param_type_ = float
                elif param_type == 'GPLong':
                    py_param_type_ = int
                elif param_type == 'GPString':
                    py_param_type_ = str
                elif param_type == 'GPDate':
                    py_param_type_ = datetime.date
                else:
                    py_param_type_ = param_type


                """
                GPDataFile	DataFile
                GPFeatureRecordSetLayer	FeatureSet
                GPLinearUnit	LinearUnit
                GPRasterData	RasterData
                GPRasterLayer	RasterData
                GPRecordSet	FeatureSet
                """ 

                if param_drtn == 'esriGPParameterDirectionInput':
                    name_type[param_name] = py_param_type_
                    print(param_name + " : " + param_type)
                    #if param_dval is not None and param_dval != '':
                    #    print(" = " + str(param_dval))
                    if param_rqrd is not None and param_rqrd == 'esriGPParameterTypeOptional':
                        print(" = None")
                    param_spec = ( param_name , param_dval )
                    spec.append(param_spec)

                    helpstring = helpstring + "   " + param_name + ": " + param['displayName']  + " (" + str(py_param_type_) + ")"
                    if param_rqrd == 'esriGPParameterTypeOptional':
                        helpstring = helpstring + " Optional parameter. "
                    elif param_rqrd == 'esriGPParameterTypeRequired':
                        helpstring = helpstring + " Required parameter. "

                    if 'description' in param:
                        helpstring = helpstring + param['description']

                elif param_drtn == 'esriGPParameterDirectionOutput':
                    name_type['return'] = py_param_type_
                    
                    helpstring = helpstring + "\nReturns " + param['displayName'] + "(" + str(py_param_type_) + ")"
                
                helpstring = helpstring + "\n"

            if 'helpUrl' in taskprops:
                helpstring = helpstring + "\nSee " + taskprops['helpUrl'] + " for additional help."
            
            generatedfn = _call_generator(task, spec)
            generatedfn.__annotations__ = name_type
            generatedfn.__doc__ = helpstring

            setattr(self, fnname, types.MethodType(generatedfn, self))

            self._method_params[task] = name_type

        # http://www.arcgis.com/home/item.html?id=383c2039b89d43baa0010c3bf243b144
        # http://sampleserver1.arcgisonline.com/ArcGIS/rest/Services/Specialty/ESRI_Currents_World/GPServer

    def __str__(self):
         return json.dumps(self)

    def _execute(self, params):
        caller_fnname = inspect.stack()[1][3]
        url = self.url + "/" + caller_fnname + "/execute"
        #print("Will call " + url +  " with these parameters:")
        
        name_type = self._method_params[caller_fnname]

        params.update({ "f" : "json" })
        for k, v in params.items():
            #print(k + " = " + str(v))
            if k in name_type:
                py_type = name_type[k]
                if py_type == 'GPFeatureRecordSetLayer':
                    geometry = v
                    val = {}
                    val['geometryType'] = 'esriGeometryPoint'
                    val['features'] = [{"geometry" : geometry}]
                    val['sr'] = {"wkid":102100,"latestWkid":3857}
                    params[k] = val
                    #params[k] = """{"geometryType":"esriGeometryPoint", "features":""" + json.dumps(geometry) + ""","sr":{"wkid":102100,"latestWkid":3857}}"""
                    #print("Updated" + k + " to " + json.dumps(params[k]))

        resp = self.item._portal.con.post(url, params)

        ret_type = name_type['return']
        try:
            geometries = []

            if ret_type == 'GPFeatureRecordSetLayer':
                #print("RESP IN GP:"+str(resp))
                value = resp['results'][0]['value']
                geom_type = value['geometryType']
                sr = value['spatialReference']

                geo_geom_type = geom_type.lower()[len("esriGeometry"):]

                features = value['features']
                geometries = []
                for feature in features:
                    geometry = feature['geometry']
                    geometry['spatialReference'] = sr
                    geometry['type'] = geo_geom_type

                    geometries.append(geometry)

            return geometries
        except:
            print("Error: " + str(resp))
            return resp
        
            
    def execute(self, task, input,
                outSR=None,
                processSR=None,
                returnZ=False,
                returnM=False):
        
        # http://sampleserver1.arcgisonline.com/ArcGIS/rest/services/Specialty/ESRI_Currents_World/GPServer/MessageInABottle/execute? Input_Point={"features":[{"geometry":{"x":0,"y":0}}]}& Days=50
        url = self.url + "/" + task + "/execute"
        params = {
            "f" : "json",
        }

        if outSR is not None:
            params['outSR'] = outSR
        if processSR is not None:
            params['processSR'] = processSR
        if returnZ:
            params['returnZ'] = "true"
        if returnM:
            params['returnM'] = "true"

        for k, v in input.items():
            params[k] = v

        resp = self.item._portal.con.post(url, params)
        return resp

    def _camelCase_to_underscore(self, name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class GeoAnalyticsTools(_AsyncService):
    "Represents the GeoAnalyticsTools service. The GeoAnalyticsTools service is provided for distributed analysis of large datasets."

    def __init__(self, url, gis):
        """
        Constructs a client to the service given it's url from ArcGIS Online or Portal.
        """
        super().__init__(url, gis)
        self.gis = gis
        params = {
            "f" : "json"
        }

    def __str__(self):
        return json.dumps(self)

    def list_bigdata_datasets(self, server_path):
        fedservers_url = self.gis._url + "portaladmin/federation/servers?f=json"
        res = self.gis._portal.con.get(fedservers_url)
        servers = res['servers']
        admin_url = _get_hosted_server_admin_url(servers)
        data_item_manifest_url = admin_url + '/data/items/bigDataFileShares/' + server_path + "/manifest"

        params = {
            'f': 'json',
        }
        res = self.gis._portal.con.post(data_item_manifest_url, params)
        
        for dataset in res['datasets']:
            print("/server/datastores/bigDataFileShares/" + server_path + '/' + dataset['path'] + 
                  ' ('+ dataset['type'] + ')')
            

    def register_bigdata_fileshare(self, server_path, fileshare_path, local_path, admin_url=None):
        #server_path = "gae3"
        #fileshare_path = "\\\\dev06999\\bigdata\\data"
        #local_path = 'C:\\bigdata\\data'

        if admin_url is None:
            fedservers_url = self.gis._url + "portaladmin/federation/servers?f=json"
            res = self.gis._portal.con.get(fedservers_url)
            servers = res['servers']
            admin_url = _get_hosted_server_admin_url(servers)

        register_data_item_url = admin_url + '/data/registerItem'

        params = {
            'f': 'json',
            'item' : {
              "path": "/bigDataFileShares",
              "type": "datadir",
              "id": "",
              "clientPath": None
            }
        }
        res = self.gis._portal.con.post(register_data_item_url, params)
        if res['success']:
            print("Created Big Data file shares data directory")
        elif res['status'] == 'exists':
            print("Big Data file share exists")

        params = {
            'f': 'json',
            'item' : {
              "path": "/fileShares/_raster_store",
              "type": "folder",
              "id": "",
              "info": {
                    "dataStoreConnectionType": "shared",
                    "path": fileshare_path
              }
            }
        }
        res = self.gis._portal.con.post(register_data_item_url, params)
        if res['success']:
            print("Created Raster Store")
        elif res['status'] == 'exists':
            print("Raster Store exists")


        params = {
            'f': 'json',
            'item' : {
              "path": "/bigDataFileShares/" + server_path,
              "type": "bigDataFileShare",
              "id": "",
              "info": {
                    "path" : fileshare_path
               }
            }
        }
        res = self.gis._portal.con.post(register_data_item_url, params)
        if res['success']:
            print("Created Big Data file share for " + server_path)
        elif res['status'] == 'exists':
            print("Big Data file share exists for " + server_path)

        manifest = self.generate_manifest(local_path)
        #print(manifest)
        manifest_upload_url =  admin_url + '/data/items/bigDataFileShares/' + server_path + '/manifest/update'

        with _tempinput(json.dumps(manifest)) as tempfilename:
            # Build the files list (tuples)
            files = []
            files.append(('manifest', tempfilename, os.path.basename(tempfilename)))
    
            postdata = {
                'f' : 'pjson'
            }
            resp = self.gis._portal.con.post(manifest_upload_url, postdata, files)
    
            if resp['status'] == 'success':
                print("Uploaded/updated manifest")


    def aggregate_points_by_bins(self,
                       in_points=None,
                       in_points_layer=None,
                       in_distance_interval=None,
                       in_timestep_interval=None,
                       in_timestep_repeat=None,
                       in_timestep_reference_time=None,
                       in_summary_stats=None,
                       out_features_name=None,
                       out_sr=None):
        """
        

        Parameters
        ----------
        in_points : Optional string
            
        in_points_layer : Optional FeatureSet
            
        in_distance_interval : Optional LinearUnit
            
        in_timestep_interval : Optional string
            
        in_timestep_repeat : Optional string
            
        in_timestep_reference_time : Optional datetime.date
            
        in_summary_stats : Optional string
            
        out_features_name : Optional string
            

        Returns
        -------
        out_sr : Optional string
            
        out_features : layer (FeatureCollection)
        """

        task ="Aggregate Points By Bins"

        params = {}

        if in_points is not None:
            params["in_points"] = in_points
        if in_points_layer is not None:
            params["in_points_layer"] = in_points_layer
        if in_distance_interval is not None:
            params["in_distance_interval"] = in_distance_interval
        if in_timestep_interval is not None:
            params["in_timestep_interval"] = in_timestep_interval
        if in_timestep_repeat is not None:
            params["in_timestep_repeat"] = in_timestep_repeat
        if in_timestep_reference_time is not None:
            params["in_timestep_reference_time"] = in_timestep_reference_time
        if in_summary_stats is not None:
            params["in_summary_stats"] = in_summary_stats
        if out_features_name is not None:
            params["out_features_name"] = out_features_name
        if out_sr is not None:
            params["outSR"] = out_sr

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['out_features']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['out_features'])


    def describe_dataset(self,
                       in_dataset=None,
                       in_dataset_layer=None,
                       out_sr=None):
        """
        

        Parameters
        ----------
        in_dataset : Optional string
            
        in_dataset_layer : Optional FeatureSet
            

        Returns
        -------
        out_sr : Optional string
            
        output_json : layer (FeatureCollection)
        """

        task ="Describe Dataset"

        params = {}

        if in_dataset is not None:
            params["in_dataset"] = in_dataset
        if in_dataset_layer is not None:
            params["in_dataset_layer"] = in_dataset_layer
        if out_sr is not None:
            params["outSR"] = out_sr

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['output_json']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['output_json'])


    def aggregate_points_by_polygons(self,
                       in_points=None,
                       in_points_layer=None,
                       in_polygons=None,
                       in_polygons_layer=None,
                       in_timestep_interval=None,
                       in_timestep_repeat=None,
                       in_timestep_reference_time=None,
                       in_summary_stats=None,
                       out_features_name=None,
                       out_sr=None):
        """
        

        Parameters
        ----------
        in_points : Optional string
            
        in_points_layer : Optional FeatureSet
            
        in_polygons : Optional string
            
        in_polygons_layer : Optional FeatureSet
            
        in_timestep_interval : Optional string
            
        in_timestep_repeat : Optional string
            
        in_timestep_reference_time : Optional datetime.date
            
        in_summary_stats : Optional string
            
        out_features_name : Optional string
            

        Returns
        -------
        out_sr : Optional string
            
        out_features : layer (FeatureCollection)
        """

        task ="Aggregate Points By Polygons"

        params = {}

        if in_points is not None:
            params["in_points"] = in_points
        if in_points_layer is not None:
            params["in_points_layer"] = in_points_layer
        if in_polygons is not None:
            params["in_polygons"] = in_polygons
        if in_polygons_layer is not None:
            params["in_polygons_layer"] = in_polygons_layer
        if in_timestep_interval is not None:
            params["in_timestep_interval"] = in_timestep_interval
        if in_timestep_repeat is not None:
            params["in_timestep_repeat"] = in_timestep_repeat
        if in_timestep_reference_time is not None:
            params["in_timestep_reference_time"] = in_timestep_reference_time
        if in_summary_stats is not None:
            params["in_summary_stats"] = in_summary_stats
        if out_features_name is not None:
            params["out_features_name"] = out_features_name
        if out_sr is not None:
            params["outSR"] = out_sr

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['out_features']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['out_features'])


    def feature_join(self,
                       in_target_features=None,
                       in_target_features_layer=None,
                       in_join_features=None,
                       in_join_features_layer=None,
                       in_join_operation="Summarize Join Features",
                       in_summary_stats=None,
                       in_spatial_relationship=None,
                       in_spatial_distance=None,
                       in_temporal_relationship=None,
                       in_temporal_distance=None,
                       in_attribute_relationship=None,
                       out_features_name=None,
                       out_sr=3857):
        """
        

        Parameters
        ----------
        in_target_features : Optional string
            
        in_target_features_layer : Optional FeatureSet
            
        in_join_features : Optional string
            
        in_join_features_layer : Optional FeatureSet
            
        in_join_operation : Optional string
            
        in_summary_stats : Optional string
            
        in_spatial_relationship : Optional string
            
        in_spatial_distance : Optional LinearUnit
            
        in_temporal_relationship : Optional string
            
        in_temporal_distance : Optional string
            
        in_attribute_relationship : Optional string
            
        out_features_name : Optional string
            
        out_sr : Optional wkid
        
        
        Returns
        -------
            
        out_features : layer (FeatureCollection)
        """

        task ="Feature Join"

        params = {}

        if in_target_features is not None:
            params["in_target_features"] = in_target_features
        if in_target_features_layer is not None:
            params["in_target_features_layer"] = in_target_features_layer
        if in_join_features is not None:
            params["in_join_features"] = in_join_features
        if in_join_features_layer is not None:
            params["in_join_features_layer"] = in_join_features_layer
        if in_join_operation is not None:
            params["in_join_operation"] = in_join_operation
        if in_summary_stats is not None:
            params["in_summary_stats"] = in_summary_stats
        if in_spatial_relationship is not None:
            params["in_spatial_relationship"] = in_spatial_relationship
        if in_spatial_distance is not None:
            params["in_spatial_distance"] = in_spatial_distance
        if in_temporal_relationship is not None:
            params["in_temporal_relationship"] = in_temporal_relationship
        if in_temporal_distance is not None:
            params["in_temporal_distance"] = in_temporal_distance
        if in_attribute_relationship is not None:
            params["in_attribute_relationship"] = in_attribute_relationship
        if out_features_name is not None:
            params["out_features_name"] = out_features_name
        if out_sr is not None:
            params["gax:env:outSR"] = out_sr

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        print(job_values)
        if out_features_name is not None:
            itemid = job_values['out_features']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            lyr = job_values['out_features']
            lyr["type"] = "FeatureLayer"
            lyr["url"] = lyr["url"] + "?token=" + self.gis._portal.con.token
            return lyr


    def create_buffers(self,
                       in_features=None,
                       in_features_layer=None,
                       in_buffer_distance=None,
                       in_buffer_distance_field=None,
                       in_method="PLANAR",
                       in_dissolve_type="NONE",
                       in_dissolve_fields=None,
                       in_summary_stats=None,
                       out_features_name=None,
                       out_sr=None):
        """
        

        Parameters
        ----------
        in_features : Optional string
            
        in_features_layer : Optional FeatureSet
            
        in_buffer_distance : Optional LinearUnit
            
        in_buffer_distance_field : Optional string
            
        in_method : Optional string
            
        in_dissolve_type : Optional string
            
        in_dissolve_fields : Optional string
            
        in_summary_stats : Optional string
            
        out_features_name : Optional string
            

        Returns
        -------
        out_sr : Optional string
            
        out_features : layer (FeatureCollection)
        """

        task ="Create Buffers"

        params = {}

        if in_features is not None:
            params["in_features"] = in_features
        if in_features_layer is not None:
            params["in_features_layer"] = in_features_layer
        if in_buffer_distance is not None:
            params["in_buffer_distance"] = in_buffer_distance
        if in_buffer_distance_field is not None:
            params["in_buffer_distance_field"] = in_buffer_distance_field
        if in_method is not None:
            params["in_method"] = in_method
        if in_dissolve_type is not None:
            params["in_dissolve_type"] = in_dissolve_type
        if in_dissolve_fields is not None:
            params["in_dissolve_fields"] = in_dissolve_fields
        if in_summary_stats is not None:
            params["in_summary_stats"] = in_summary_stats
        if out_features_name is not None:
            params["out_features_name"] = out_features_name
        if out_sr is not None:
            params["outSR"] = out_sr

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['out_features']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['out_features'])


    def point_density(self,
                       in_points=None,
                       in_points_layer=None,
                       in_population_field=None,
                       in_cell_size=None,
                       in_neighborhood="Circle",
                       in_neighborhood_size=None,
                       out_features_name=None,
                       out_sr=None):
        """
        

        Parameters
        ----------
        in_points : Optional string
            
        in_points_layer : Optional FeatureSet
            
        in_population_field : Optional string
            
        in_cell_size : Optional LinearUnit
            
        in_neighborhood : Optional string
            
        in_neighborhood_size : Optional string
            
        out_features_name : Optional string
            

        Returns
        -------
        out_sr : Optional string
            
        out_features : layer (FeatureCollection)
        """

        task ="Point Density"

        params = {}

        if in_points is not None:
            params["in_points"] = in_points
        if in_points_layer is not None:
            params["in_points_layer"] = in_points_layer
        if in_population_field is not None:
            params["in_population_field"] = in_population_field
        if in_cell_size is not None:
            params["in_cell_size"] = in_cell_size
        if in_neighborhood is not None:
            params["in_neighborhood"] = in_neighborhood
        if in_neighborhood_size is not None:
            params["in_neighborhood_size"] = in_neighborhood_size
        if out_features_name is not None:
            params["out_features_name"] = out_features_name
        if out_sr is not None:
            params["outSR"] = out_sr

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['out_features']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['out_features'])


    def create_raster(self,
                       in_features=None,
                       in_features_layer=None,
                       in_cell_size=None,
                       out_sr=None):
        """
        

        Parameters
        ----------
        in_features : Optional string
            
        in_features_layer : Optional FeatureSet
            
        in_cell_size : Optional LinearUnit
            

        Returns
        -------
        out_sr : Optional string
            
        out_crf : layer (FeatureCollection)
        """

        task ="Create Raster"

        params = {}

        if in_features is not None:
            params["in_features"] = in_features
        if in_features_layer is not None:
            params["in_features_layer"] = in_features_layer
        if in_cell_size is not None:
            params["in_cell_size"] = in_cell_size
        if out_sr is not None:
            params["outSR"] = out_sr

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['out_crf']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['out_crf'])


    def extract_data(self,
                       in_features=None,
                       in_features_layer=None,
                       in_start_date=None,
                       in_end_date=None,
                       out_features_name=None,
                       out_sr=None):
        """
        

        Parameters
        ----------
        in_features : Optional string
            
        in_features_layer : Optional FeatureSet
            
        in_start_date : Optional datetime.date
            
        in_end_date : Optional datetime.date
            
        out_features_name : Optional string
            

        Returns
        -------
        out_sr : Optional string
            
        out_features : layer (FeatureCollection)
        """

        task ="Extract Data"

        params = {}

        if in_features is not None:
            params["in_features"] = in_features
        if in_features_layer is not None:
            params["in_features_layer"] = in_features_layer
        if in_start_date is not None:
            params["in_start_date"] = in_start_date
        if in_end_date is not None:
            params["in_end_date"] = in_end_date
        if out_features_name is not None:
            params["out_features_name"] = out_features_name
        if out_sr is not None:
            params["outSR"] = out_sr

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['out_features']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['out_features'])


    def reconstruct_tracks(self,
                       in_features=None,
                       in_features_layer=None,
                       in_track_fields=None,
                       in_method="PLANAR",
                       in_buffer_distance_field=None,
                       in_summary_stats=None,
                       in_distance_split=None,
                       in_duration_split=None,
                       out_features=None,
                       out_sr=None):
        """
        

        Parameters
        ----------
        in_features : Optional string
            
        in_features_layer : Optional FeatureSet
            
        in_track_fields : Optional string
            
        in_method : Optional string
            
        in_buffer_distance_field : Optional string
            
        in_summary_stats : Optional string
            
        in_distance_split : Optional LinearUnit
            
        in_duration_split : Optional string
            
        out_features : Optional string
            
        out_sr : Optional wkid

        Returns
        -------
            
        out_features : layer
        """

        task ="Reconstruct Tracks"

        params = {}

        if in_features is not None:
            params["in_features"] = in_features
        if in_features_layer is not None:
            params["in_features_layer"] = in_features_layer
        if in_track_fields is not None:
            params["in_track_fields"] = in_track_fields
        if in_method is not None:
            params["in_method"] = in_method
        if in_buffer_distance_field is not None:
            params["in_buffer_distance_field"] = in_buffer_distance_field
        if in_summary_stats is not None:
            params["in_summary_stats"] = in_summary_stats
        if in_distance_split is not None:
            params["in_distance_split"] = in_distance_split
        if in_duration_split is not None:
            params["in_duration_split"] = in_duration_split
        if out_features is not None:
            params["out_features_name"] = out_features
        if out_sr is not None:
            params["outSR"] = out_sr

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        print(job_values)
        if out_features is not None:
            itemid = job_values['out_features']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            lyr = job_values['out_features']
            
            lyr["type"] = "FeatureLayer"
            #lyr["url"] = lyr["url"] + "?token=" + self.gis._portal.con.token

            flurl = lyr['url']
            print("FL URL: "+ flurl)
            fsurl = flurl[:-2]
            print("FS URL: " +fsurl)
            params = {
                "f" : "json"
            }

            layerdata = self.gis._portal.con.post(flurl, params)
            
            layer = Layer(fsurl, layerdata, None, self.gis)
            return layer


    def create_space_time_cube(self,
                       in_features=None,
                       in_features_layer=None,
                       in_bin_size=None,
                       in_slice_size=None,
                       out_sr=None):
        """
        

        Parameters
        ----------
        in_features : Optional string
            
        in_features_layer : Optional FeatureSet
            
        in_bin_size : Optional LinearUnit
            
        in_slice_size : Optional string
            

        Returns
        -------
        out_sr : Optional string
            
        out_cube : layer (FeatureCollection)
        """

        task ="Create Space Time Cube"

        params = {}

        if in_features is not None:
            params["in_features"] = in_features
        if in_features_layer is not None:
            params["in_features_layer"] = in_features_layer
        if in_bin_size is not None:
            params["in_bin_size"] = in_bin_size
        if in_slice_size is not None:
            params["in_slice_size"] = in_slice_size
        if out_sr is not None:
            params["outSR"] = out_sr

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['out_cube']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['out_cube'])


    def sandbox(self,
                       command=None,
                       arg=None,
                       out_sr=None):
        """
        

        Parameters
        ----------
        command : Optional string
            
        arg : Optional string
            
        out_sr : Optional string
            
        """

        task ="Sandbox"

        params = {}

        if command is not None:
            params["command"] = command
        if arg is not None:
            params["arg"] = arg
        if out_sr is not None:
            params["outSR"] = out_sr
            return { }


    def create_panel_data(self,
                       in_target_features=None,
                       in_target_features_layer=None,
                       in_join_features=None,
                       in_join_features_layer=None,
                       in_summary_stats=None,
                       in_spatial_relationship=None,
                       in_spatial_distance=None,
                       in_attribute_relationship=None,
                       in_panel_timestep_interval=None,
                       in_panel_timestep_repeat=None,
                       in_panel_reference_time=None,
                       out_features_name=None,
                       out_sr=None):
        """
        

        Parameters
        ----------
        in_target_features : Optional string
            
        in_target_features_layer : Optional FeatureSet
            
        in_join_features : Optional string
            
        in_join_features_layer : Optional FeatureSet
            
        in_summary_stats : Optional string
            
        in_spatial_relationship : Optional string
            
        in_spatial_distance : Optional LinearUnit
            
        in_attribute_relationship : Optional string
            
        in_panel_timestep_interval : Optional string
            
        in_panel_timestep_repeat : Optional string
            
        in_panel_reference_time : Optional datetime.date
            
        out_features_name : Optional string
            

        Returns
        -------
        out_sr : Optional string
            
        out_features : layer (FeatureCollection)
        """

        task ="Create Panel Data"

        params = {}

        if in_target_features is not None:
            params["in_target_features"] = in_target_features
        if in_target_features_layer is not None:
            params["in_target_features_layer"] = in_target_features_layer
        if in_join_features is not None:
            params["in_join_features"] = in_join_features
        if in_join_features_layer is not None:
            params["in_join_features_layer"] = in_join_features_layer
        if in_summary_stats is not None:
            params["in_summary_stats"] = in_summary_stats
        if in_spatial_relationship is not None:
            params["in_spatial_relationship"] = in_spatial_relationship
        if in_spatial_distance is not None:
            params["in_spatial_distance"] = in_spatial_distance
        if in_attribute_relationship is not None:
            params["in_attribute_relationship"] = in_attribute_relationship
        if in_panel_timestep_interval is not None:
            params["in_panel_timestep_interval"] = in_panel_timestep_interval
        if in_panel_timestep_repeat is not None:
            params["in_panel_timestep_repeat"] = in_panel_timestep_repeat
        if in_panel_reference_time is not None:
            params["in_panel_reference_time"] = in_panel_reference_time
        if out_features_name is not None:
            params["out_features_name"] = out_features_name
        if out_sr is not None:
            params["gax:env:outSR"] = out_sr

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['out_features']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['out_features'])


    def generate_manifest(self,
                       in_datastore_folder=None,
                       out_sr=None):
        """
        

        Parameters
        ----------
        in_datastore_folder : Optional string
            

        Returns
        -------
        out_sr : Optional string
            
        out_manifest_json : layer (FeatureCollection)
        """

        task ="Generate Manifest"

        params = {}

        if in_datastore_folder is not None:
            params["in_datastore_folder"] = in_datastore_folder
        if out_sr is not None:
            params["outSR"] = out_sr

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        
        res = job_values['out_manifest_json']
        
        manifest_url = res['url']
        manifest = self.gis._portal.con.get(manifest_url)
        #print("FETCHED" + json.dumps(manifest))
        return manifest

class SpatialAnalysisTools(_AsyncService):
    "Represents the SpatialAnalysisTools service. The SpatialAnalysisTools service is used for supporting Spatial analysis capability in Portal for ArcGIS."

    def __init__(self, url, gis):
        """
        Constructs a client to the service given it's url from ArcGIS Online or Portal.
        """
        super().__init__(url, gis)
        
        params = {
            "f" : "json"
        }

    def __str__(self):
        return json.dumps(self)

    


    def aggregate_points(self,
                       point_layer,
                       polygon_layer,
                       keep_boundaries_with_no_points=True,
                       summary_fields=[],
                       group_by_field=None,
                       minority_majority=False,
                       percent_points=False,
                       output_name=None,
                       context=None):
        """
        Aggregate points task allows you to aggregate or count the total number of points that are distributed within specified areas or boundaries (polygons). You can also summarize Sum, Mean, Min, Max and Standard deviation calculations for attributes of the point layer to understand the general characteristics of aggregated points. 

        Parameters
        ----------
        point_layer : Required layer (see Feature Input in documentation)
            Point layer to be aggregated
        polygon_layer : Required layer (see Feature Input in documentation)
            Polygon layer to which the points should be aggregated.
        keep_boundaries_with_no_points : Optional bool
            Specify whether the polygons without any points should be returned in the output.
        summary_fields : Optional list of strings
            A list of field names and summary type. Example [fieldName1 summaryType1,fieldName2 summaryType2].
        group_by_field : Optional string
            A field name from PointLayer based on which the points will be grouped.
        minority_majority : Optional bool
            This boolean parameter is applicable only when a groupByField is specified. If true, the minority (least dominant) or the majority (most dominant) attribute values within each group, within each boundary will be calculated.
        percent_points : Optional bool
            This boolean parameter is applicable only when a groupByField is specified. If set to true, the percentage count of points for each unique groupByField value is calculated.
        output_name : Optional string
            Additional properties such as output feature service name.
        context : Optional string
            Additional settings such as processing extent and output spatial reference.

        Returns
        -------
        dict with the following keys:
           "aggregated_layer" : layer (FeatureCollection)
           "group_summary" : layer (FeatureCollection)
        """

        task ="AggregatePoints"

        params = {}

        params["pointLayer"] = super()._feature_input(point_layer)
        params["polygonLayer"] = super()._feature_input(polygon_layer)
        if keep_boundaries_with_no_points is not None:
            params["keepBoundariesWithNoPoints"] = keep_boundaries_with_no_points
        if summary_fields is not None:
            params["summaryFields"] = summary_fields
        if group_by_field is not None:
            params["groupByField"] = group_by_field
        if minority_majority is not None:
            params["minorityMajority"] = minority_majority
        if percent_points is not None:
            params["percentPoints"] = percent_points
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['aggregatedLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            
            aggregated_layer = FeatureCollection(job_values['aggregatedLayer'])

            group_summary = FeatureCollection(job_values['groupSummary'])
            return { "aggregated_layer":aggregated_layer, "group_summary":group_summary, }


    def find_hot_spots(self,
                       analysis_layer,
                       analysis_field=None,
                       divided_by_field=None,
                       bounding_polygon_layer=None,
                       aggregation_polygon_layer=None,
                       output_name=None,
                       context=None):
        """
        The Find Hot Spots task finds statistically significant clusters of incident points, weighted points, or weighted polygons. For incident data, the analysis field (weight) is obtained by aggregation. Output is a hot spot map.

        Parameters
        ----------
        analysis_layer : Required layer (see Feature Input in documentation)
            The point or polygon feature layer for which hot spots will be calculated.
        analysis_field : Optional string
            The numeric field in the AnalysisLayer that will be analyzed. 
        divided_by_field : Optional string
            
        bounding_polygon_layer : Optional layer (see Feature Input in documentation)
            When the analysis layer is points and no AnalysisField is specified, you can provide polygons features that define where incidents could have occurred.
        aggregation_polygon_layer : Optional layer (see Feature Input in documentation)
            When the AnalysisLayer contains points and no AnalysisField is specified, you can provide polygon features into which the points will be aggregated and analyzed, such as administrative units.
        output_name : Optional string
            Additional properties such as output feature service name.
        context : Optional string
            Additional settings such as processing extent and output spatial reference.

        Returns
        -------
        dict with the following keys:
           "hot_spots_result_layer" : layer (FeatureCollection)
           "process_info" : list of messages
        """

        task ="FindHotSpots"

        params = {}

        params["analysisLayer"] = super()._feature_input(analysis_layer)
        if analysis_field is not None:
            params["analysisField"] = analysis_field
        if divided_by_field is not None:
            params["dividedByField"] = divided_by_field
        if bounding_polygon_layer is not None:
            params["boundingPolygonLayer"] = super()._feature_input(bounding_polygon_layer)
        if aggregation_polygon_layer is not None:
            params["aggregationPolygonLayer"] = super()._feature_input(aggregation_polygon_layer)
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['hotSpotsResultLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            
            hot_spots_result_layer = FeatureCollection(job_values['hotSpotsResultLayer'])

            process_info = job_values['processInfo']
            return { "hot_spots_result_layer":hot_spots_result_layer, "process_info":process_info, }


    def create_buffers(self,
                       input_layer,
                       distances=[],
                       field=None,
                       units="Meters",
                       dissolve_type="None",
                       ring_type="Disks",
                       side_type="Full",
                       end_type="Round",
                       output_name=None,
                       context=None):
        """
        Creates buffer polygon(s) around input features.

        Parameters
        ----------
        input_layer : Required layer (see Feature Input in documentation)
            The input to be buffered.
        distances : Optional list of floats
            The distance(s) that will be buffered.
        field : Optional string
            Buffers will be created using field values.
        units : Optional string
            The linear unit to be used with the distance value(s).
        dissolve_type : Optional string
            Specifies the dissolve to be performed to remove buffer overlap.
        ring_type : Optional string
            The ring type.
        side_type : Optional string
            The side(s) of the input that will be buffered.
        end_type : Optional string
            The shape of the buffer at the end of buffered line features.
        output_name : Optional string
            Additional properties such as output feature service name.
        context : Optional string
            Additional settings such as processing extent and output spatial reference.

        Returns
        -------
        buffer_layer : layer (FeatureCollection)
        """

        task ="CreateBuffers"

        params = {}

        params["inputLayer"] = super()._feature_input(input_layer)
        if distances is not None:
            params["distances"] = distances
        if field is not None:
            params["field"] = field
        if units is not None:
            params["units"] = units
        if dissolve_type is not None:
            params["dissolveType"] = dissolve_type
        if ring_type is not None:
            params["ringType"] = ring_type
        if side_type is not None:
            params["sideType"] = side_type
        if end_type is not None:
            params["endType"] = end_type
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['bufferLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['bufferLayer'])


    def create_drive_time_areas(self,
                       input_layer,
                       break_values=[5, 10, 15],
                       break_units="Minutes",
                       travel_mode="Driving",
                       overlap_policy="Overlap",
                       time_of_day=None,
                       time_zone_for_time_of_day="GeoLocal",
                       output_name=None,
                       context=None):
        """
        

        Parameters
        ----------
        input_layer : Required layer (see Feature Input in documentation)
            
        break_values : Optional list of floats
            
        break_units : Optional string
            
        travel_mode : Optional string
            
        overlap_policy : Optional string
            
        time_of_day : Optional datetime.date
            
        time_zone_for_time_of_day : Optional string
            
        output_name : Optional string
            Additional properties such as output feature service name.
        context : Optional string
            Additional settings such as processing extent and output spatial reference.

        Returns
        -------
        drive_time_areas_layer : layer (FeatureCollection)
        """

        task ="CreateDriveTimeAreas"

        params = {}

        params["inputLayer"] = super()._feature_input(input_layer)
        if break_values is not None:
            params["breakValues"] = break_values
        if break_units is not None:
            params["breakUnits"] = break_units
        if travel_mode is not None:
            params["travelMode"] = travel_mode
        if overlap_policy is not None:
            params["overlapPolicy"] = overlap_policy
        if time_of_day is not None:
            params["timeOfDay"] = time_of_day
        if time_zone_for_time_of_day is not None:
            params["timeZoneForTimeOfDay"] = time_zone_for_time_of_day
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['driveTimeAreasLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['driveTimeAreasLayer'])


    def dissolve_boundaries(self,
                       input_layer,
                       dissolve_fields=[],
                       summary_fields=[],
                       output_name=None,
                       context=None):
        """
        Dissolve features based on specified fields.

        Parameters
        ----------
        input_layer : Required layer (see Feature Input in documentation)
            The layer containing polygon features that will be dissolved.
        dissolve_fields : Optional list of strings
            One or more fields from the input that control which polygons are merged. If no fields are supplied, all polygons that overlap or shared a common border will be dissolved into one polygon.
        summary_fields : Optional list of strings
            A list of field names and statistical types that will be used to summarize the output. Supported statistics include: Sum, Mean, Min, Max, and Stddev.
        output_name : Optional string
            Additional properties such as output feature service name.
        context : Optional string
            Additional settings such as processing extent and output spatial reference.

        Returns
        -------
        dissolved_layer : layer (FeatureCollection)
        """

        task ="DissolveBoundaries"

        params = {}

        params["inputLayer"] = super()._feature_input(input_layer)
        if dissolve_fields is not None:
            params["dissolveFields"] = dissolve_fields
        if summary_fields is not None:
            params["summaryFields"] = summary_fields
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['dissolvedLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['dissolvedLayer'])


    def merge_layers(self,
                       input_layer,
                       merge_layer,
                       merging_attributes=[],
                       output_name=None,
                       context=None):
        """
        Combines two inputs of the same feature data type into a new output.

        Parameters
        ----------
        input_layer : Required layer (see Feature Input in documentation)
             The point, line, or polygon  features to merge with the mergeLayer.
        merge_layer : Required layer (see Feature Input in documentation)
            The point, line or polygon features to merge with inputLayer.  mergeLayer must contain the same feature type (point, line, or polygon) as the inputLayer.
        merging_attributes : Optional list of strings
            An array of values that describe how fields from the mergeLayer are to be modified.  By default all fields from both inputs will be carried across to the output.
        output_name : Optional string
            Additional properties such as output feature service name.
        context : Optional string
            Additional settings such as processing extent and output spatial reference.

        Returns
        -------
        merged_layer : layer (FeatureCollection)
        """

        task ="MergeLayers"

        params = {}

        params["inputLayer"] = super()._feature_input(input_layer)
        params["mergeLayer"] = super()._feature_input(merge_layer)
        if merging_attributes is not None:
            params["mergingAttributes"] = merging_attributes
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['mergedLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['mergedLayer'])


    def summarize_within(self,
                       sum_within_layer,
                       summary_layer,
                       sum_shape=True,
                       shape_units=None,
                       summary_fields=[],
                       group_by_field=None,
                       minority_majority=False,
                       percent_shape=False,
                       output_name=None,
                       context=None):
        """
        The SummarizeWithin task helps you to summarize and find statistics on the point, line, or polygon features (or portions of these features) that are within the boundaries of polygons in another layer. For example:Given a layer of watershed boundaries and a layer of land-use boundaries by land-use type, calculate total acreage of land-use type for each watershed.Given a layer of parcels in a county and a layer of city boundaries, summarize the average value of vacant parcels within each city boundary.Given a layer of counties and a layer of roads, summarize the total mileage of roads by road type within each county.

        Parameters
        ----------
        sum_within_layer : Required layer (see Feature Input in documentation)
            A polygon feature layer or featurecollection. Features, or portions of features, in the summaryLayer (below) that fall within the boundaries of these polygons will be summarized.
        summary_layer : Required layer (see Feature Input in documentation)
            Point, line, or polygon features that will be summarized for each polygon in the sumWithinLayer.
        sum_shape : Optional bool
            A boolean value that instructs the task to calculate count of points, length of lines or areas of polygons of the summaryLayer within each polygon in sumWithinLayer.
        shape_units : Optional string
            Specify units to summarize the length or areas when sumShape is set to true. Units is not required to summarize points.
        summary_fields : Optional list of strings
            A list of field names and statistical summary type that you wish to calculate for all features in the  summaryLayer that are within each polygon in the sumWithinLayer . Eg: ["fieldname1 summary", "fieldname2 summary"]
        group_by_field : Optional string
            Specify a field from the summaryLayer features to calculate statistics separately for each unique attribute value.
        minority_majority : Optional bool
            This boolean parameter is applicable only when a groupByField is specified. If true, the minority (least dominant) or the majority (most dominant) attribute values within each group, within each boundary will be calculated. 
        percent_shape : Optional bool
            This boolean parameter is applicable only when a groupByField is specified. If set to true, the percentage of shape (eg. length for lines) for each unique groupByField value is calculated.
        output_name : Optional string
            Additional properties such as output feature service name.
        context : Optional string
            Additional settings such as processing extent and output spatial reference.

        Returns
        -------
        dict with the following keys:
           "result_layer" : layer (FeatureCollection)
           "group_by_summary" : layer (FeatureCollection)
        """

        task ="SummarizeWithin"

        params = {}

        params["sumWithinLayer"] = super()._feature_input(sum_within_layer)
        params["summaryLayer"] = super()._feature_input(summary_layer)
        if sum_shape is not None:
            params["sumShape"] = sum_shape
        if shape_units is not None:
            params["shapeUnits"] = shape_units
        if summary_fields is not None:
            params["summaryFields"] = summary_fields
        if group_by_field is not None:
            params["groupByField"] = group_by_field
        if minority_majority is not None:
            params["minorityMajority"] = minority_majority
        if percent_shape is not None:
            params["percentShape"] = percent_shape
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['resultLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            
            result_layer = FeatureCollection(job_values['resultLayer'])

            group_by_summary = FeatureCollection(job_values['groupBySummary'])
            return { "result_layer":result_layer, "group_by_summary":group_by_summary, }


    def enrich_layer(self,
                       input_layer,
                       data_collections=[],
                       analysis_variables=[],
                       country=None,
                       buffer_type=None,
                       distance=None,
                       units=None,
                       output_name=None,
                       context=None):
        """
        The Enrich Layer task enriches your data by getting facts about the people, places, and businesses that surround your data locations. For example: What kind of people live here? What do people like to do in this area? What are their habits and lifestyles? What kind of businesses are there in this area?The result will be a new layer of input features that includes all demographic and geographic information from given data collections. 

        Parameters
        ----------
        input_layer : Required layer (see Feature Input in documentation)
            Feature layer to enrich with new data
        data_collections : Optional list of strings
            Data collections you wish to add to your features.
        analysis_variables : Optional list of strings
            A subset of specific variables instead of dataCollections.
        country : Optional string
            The two character country code that specifies the country of the input features. Eg. US (United States),  FR (France), GB (United Kingdom) etc.
        buffer_type : Optional string
            Area to be created around the point or line features for enrichment. Default is 1 Mile straight-line buffer radius.
        distance : Optional float
            A double value that defines the straight-line distance or time (when drivingTime is used).
        units : Optional string
            The unit (eg. Miles, Minutes) to be used with the distance value(s) specified in the distance parameter to calculate the area.
        output_name : Optional string
            Additional properties such as output feature service name.
        context : Optional string
            Additional settings such as processing extent and output spatial reference.

        Returns
        -------
        enriched_layer : layer (FeatureCollection)
        """

        task ="EnrichLayer"

        params = {}

        params["inputLayer"] = super()._feature_input(input_layer)
        if data_collections is not None:
            params["dataCollections"] = data_collections
        if analysis_variables is not None:
            params["analysisVariables"] = analysis_variables
        if country is not None:
            params["country"] = country
        if buffer_type is not None:
            params["bufferType"] = buffer_type
        if distance is not None:
            params["distance"] = distance
        if units is not None:
            params["units"] = units
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['enrichedLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['enrichedLayer'])


    def overlay_layers(self,
                       input_layer,
                       overlay_layer,
                       overlay_type="Intersect",
                       snap_to_input=False,
                       output_type="Input",
                       tolerance=None,
                       output_name=None,
                       context=None):
        """
        Overlays the input layer with the overlay layer. Overlay operations supported are Intersect, Union, and Erase.

        Parameters
        ----------
        input_layer : Required layer (see Feature Input in documentation)
            The input analysis layer.
        overlay_layer : Required layer (see Feature Input in documentation)
            The layer to be overlaid with the analysis layer.
        overlay_type : Optional string
            The overlay type (INTERSECT, UNION, or ERASE) defines how the analysis layer and the overlay layer are combined.
        snap_to_input : Optional bool
            When the distance between features is less than the tolerance, the features in the overlay layer will snap to the features in the input layer.
        output_type : Optional string
            The type of intersection (INPUT, LINE, POINT).
        tolerance : Optional float
            The minimum distance separating all feature coordinates (nodes and vertices) as well as the distance a coordinate can move in X or Y (or both). 
        output_name : Optional string
            Additional properties such as output feature service name.
        context : Optional string
            Additional settings such as processing extent and output spatial reference.

        Returns
        -------
        output_layer : layer (FeatureCollection)
        """

        task ="OverlayLayers"

        params = {}

        params["inputLayer"] = super()._feature_input(input_layer)
        params["overlayLayer"] = super()._feature_input(overlay_layer)
        if overlay_type is not None:
            params["overlayType"] = overlay_type
        if snap_to_input is not None:
            params["snapToInput"] = snap_to_input
        if output_type is not None:
            params["outputType"] = output_type
        if tolerance is not None:
            params["tolerance"] = tolerance
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['outputLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['outputLayer'])


    def extract_data(self,
                       input_layers=[],
                       extent=None,
                       clip=False,
                       data_format=None,
                       output_name=None,
                       context=None):
        """
        Select and download data for a specified area of interest. Layers that you select will be added to a zip file or layer package. 

        Parameters
        ----------
        input_layers : Required list of strings
            The layers from which you can extract features. 
        extent : Optional string
            The area that defines which features will be included in the output zip file or layer package.   
        clip : Optional bool
            Select features that intersect the extent or clip features within the extent.
        data_format : Optional string
            Format of the data that will be extracted and downloaded.  Layer packages will always include file geodatabases.&lt;/p&gt;
        output_name : Optional string
            Additional properties such as output feature service name.
        context : Optional string
            Additional settings such as processing extent and output spatial reference.

        Returns
        -------
        content_id : layer (FeatureCollection)
        """

        task ="ExtractData"

        params = {}

        params["inputLayers"] = input_layers
        if extent is not None:
            params["extent"] = extent
        if clip is not None:
            params["clip"] = clip
        if data_format is not None:
            params["dataFormat"] = data_format
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['contentID']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['contentID'])


    def find_existing_locations(self,
                       input_layers=[],
                       expressions=[],
                       output_name=None,
                       context=None):
        """
        The Find Existing Locations task selects features in the input layer that meet a query you specify. A query is made up of one or more expressions. There are two types of expressions: attribute and spatial. An example of an attribute expression is that a parcel must be vacant, which is an attribute of the Parcels layer (where STATUS = 'VACANT'). An example of a spatial expression is that the parcel must also be within a certain distance of a river (Parcels within a distance of 0.75 Miles from Rivers).

        Parameters
        ----------
        input_layers : Required list of strings
            A list of layers that will be used in the expressions parameter.
        expressions : Required string
            Specify a list of expressions. Please refer documentation at http://developers.arcgis.com for more information on creating expressions.
        output_name : Optional string
            Additional properties such as output feature service name.
        context : Optional string
            Additional settings such as processing extent and output spatial reference.

        Returns
        -------
        result_layer : layer (FeatureCollection)
        """

        task ="FindExistingLocations"

        params = {}

        params["inputLayers"] = input_layers
        params["expressions"] = expressions
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['resultLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['resultLayer'])


    def derive_new_locations(self,
                       input_layers=[],
                       expressions=[],
                       output_name=None,
                       context=None):
        """
        The Derive New Locations task derives new features from the input layers that meet a query you specify. A query is made up of one or more expressions. There are two types of expressions: attribute and spatial. An example of an attribute expression is that a parcel must be vacant, which is an attribute of the Parcels layer (where STATUS = 'VACANT'). An example of a spatial expression is that the parcel must also be within a certain distance of a river (Parcels within a distance of 0.75 Miles from Rivers).The Derive New Locations task is very similar to the Find Existing Locations task, the main difference is that the result of Derive New Locations can contain partial features.In both tasks, the attribute expression  where and the spatial relationships within and contains return the same result. This is because these relationships return entire features.When intersects or withinDistance is used, Derive New Locations creates new features in the result. For example, when intersecting a parcel feature and a flood zone area that partially overlap each other, Find Existing Locations will return the entire parcel whereas Derive New Locations will return just the portion of the parcel that is within the flood zone.

        Parameters
        ----------
        input_layers : Required list of strings
            A list of layers that will be used in the expressions parameter.
        expressions : Required string
            Specify a list of expressions. Please refer documentation at http://developers.arcgis.com for more information on expressions.
        output_name : Optional string
            Additional properties such as output feature service name.
        context : Optional string
            Additional settings such as processing extent and output spatial reference.

        Returns
        -------
        result_layer : layer (FeatureCollection)
        """

        task ="DeriveNewLocations"

        params = {}

        params["inputLayers"] = input_layers
        params["expressions"] = expressions
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['resultLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['resultLayer'])


    def field_calculator(self,
                       input_layer,
                       expressions,
                       output_name=None,
                       context=None):
        """
        Calculates existing fields or creates and calculates new fields.

        Parameters
        ----------
        input_layer : Required layer (see Feature Input in documentation)
            
        expressions : Required string
            
        output_name : Optional string
            
        context : Optional string
            

        Returns
        -------
        result_layer : layer (FeatureCollection)
        """

        task ="FieldCalculator"

        params = {}

        params["inputLayer"] = super()._feature_input(input_layer)
        params["expressions"] = expressions
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['resultLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['resultLayer'])


    def interpolate_points(self,
                       input_layer,
                       field,
                       interpolate_option="5",
                       output_prediction_error=False,
                       classification_type="GeometricInterval",
                       num_classes=10,
                       class_breaks=[],
                       bounding_polygon_layer=None,
                       predict_at_point_layer=None,
                       output_name=None,
                       context=None):
        """
        The Interpolate Points task allows you to predict values at new locations based on measurements from a collection of points. The task takes point data with values at each point and returns areas classified by predicted values. 

        Parameters
        ----------
        input_layer : Required layer (see Feature Input in documentation)
            The point layer whose features will be interpolated.
        field : Required string
            Name of the numeric field containing the values you wish to interpolate.
        interpolate_option : Optional string
            Integer value declaring your preference for speed versus accuracy, from 1 (fastest) to 9 (most accurate). More accurate predictions take longer to calculate.
        output_prediction_error : Optional bool
            If True, a polygon layer of standard errors for the interpolation predictions will be returned in the predictionError output parameter.
        classification_type : Optional string
            Determines how predicted values will be classified into areas.
        num_classes : Optional int
            This value is used to divide the range of interpolated values into distinct classes. The range of values in each class is determined by the classificationType parameter. Each class defines the boundaries of the result polygons.
        class_breaks : Optional list of floats
            If classificationType is Manual, supply desired class break values separated by spaces. These values define the upper limit of each class, so the number of classes will equal the number of entered values. Areas will not be created for any locations with predicted values above the largest entered break value. You must enter at least two values and no more than 32.
        bounding_polygon_layer : Optional layer (see Feature Input in documentation)
            A layer specifying the polygon(s) where you want values to be interpolated.
        predict_at_point_layer : Optional layer (see Feature Input in documentation)
            An optional layer specifying point locations to calculate prediction values. This allows you to make predictions at specific locations of interest. 
        output_name : Optional string
            Additional properties such as output feature service name.
        context : Optional string
            Additional settings such as processing extent and output spatial reference.

        Returns
        -------
        dict with the following keys:
           "result_layer" : layer (FeatureCollection)
           "prediction_error" : layer (FeatureCollection)
           "predicted_point_layer" : layer (FeatureCollection)
        """

        task ="InterpolatePoints"

        params = {}

        params["inputLayer"] = super()._feature_input(input_layer)
        params["field"] = field
        if interpolate_option is not None:
            params["interpolateOption"] = interpolate_option
        if output_prediction_error is not None:
            params["outputPredictionError"] = output_prediction_error
        if classification_type is not None:
            params["classificationType"] = classification_type
        if num_classes is not None:
            params["numClasses"] = num_classes
        if class_breaks is not None:
            params["classBreaks"] = class_breaks
        if bounding_polygon_layer is not None:
            params["boundingPolygonLayer"] = super()._feature_input(bounding_polygon_layer)
        if predict_at_point_layer is not None:
            params["predictAtPointLayer"] = super()._feature_input(predict_at_point_layer)
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['resultLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            
            result_layer = FeatureCollection(job_values['resultLayer'])

            prediction_error = FeatureCollection(job_values['predictionError'])

            predicted_point_layer = FeatureCollection(job_values['predictedPointLayer'])
            return { "result_layer":result_layer, "prediction_error":prediction_error, "predicted_point_layer":predicted_point_layer, }


    def calculate_density(self,
                       input_layer,
                       field=None,
                       cell_size=None,
                       cell_size_units="Meters",
                       radius=None,
                       radius_units=None,
                       bounding_polygon_layer=None,
                       area_units=None,
                       classification_type="EqualInterval",
                       num_classes=10,
                       output_name=None,
                       context=None):
        """
        The Calculate Density task creates a density map from point or line features by spreading known quantities of some phenomenon (represented as attributes of the points or lines) across the map. The result is a layer of areas classified from least dense to most dense.

        Parameters
        ----------
        input_layer : Required layer (see Feature Input in documentation)
            The point or line features from which to calculate density.
        field : Optional string
            A numeric field name specifying the number of incidents at each location. If not specified, each location will be assumed to represent a single count.
        cell_size : Optional float
            This value is used to create a mesh of points where density values are calculated. The default is approximately 1/1000th of the smaller of the width and height of the analysis extent as defined in the context parameter.
        cell_size_units : Optional string
            The units of the cellSize value
        radius : Optional float
            A distance specifying how far to search to find point or line features when calculating density values.
        radius_units : Optional string
            The units of the radius parameter. 
        bounding_polygon_layer : Optional layer (see Feature Input in documentation)
            A layer specifying the polygon(s) where you want densities to be calculated.
        area_units : Optional string
            The units of the calculated density values.
        classification_type : Optional string
            Determines how density values will be classified into polygons.
        num_classes : Optional int
            This value is used to divide the range of predicted values into distinct classes. The range of values in each class is determined by the classificationType parameter.
        output_name : Optional string
            Additional properties such as output feature service name.
        context : Optional string
            Additional settings such as processing extent and output spatial reference.

        Returns
        -------
        result_layer : layer (FeatureCollection)
        """

        task ="CalculateDensity"

        params = {}

        params["inputLayer"] = super()._feature_input(input_layer)
        if field is not None:
            params["field"] = field
        if cell_size is not None:
            params["cellSize"] = cell_size
        if cell_size_units is not None:
            params["cellSizeUnits"] = cell_size_units
        if radius is not None:
            params["radius"] = radius
        if radius_units is not None:
            params["radiusUnits"] = radius_units
        if bounding_polygon_layer is not None:
            params["boundingPolygonLayer"] = super()._feature_input(bounding_polygon_layer)
        if area_units is not None:
            params["areaUnits"] = area_units
        if classification_type is not None:
            params["classificationType"] = classification_type
        if num_classes is not None:
            params["numClasses"] = num_classes
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['resultLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['resultLayer'])


    def summarize_nearby(self,
                       sum_nearby_layer,
                       summary_layer,
                       near_type="StraightLine",
                       distances=[],
                       units="Meters",
                       time_of_day=None,
                       time_zone_for_time_of_day="GeoLocal",
                       return_boundaries=True,
                       sum_shape=True,
                       shape_units=None,
                       summary_fields=[],
                       group_by_field=None,
                       minority_majority=False,
                       percent_shape=False,
                       output_name=None,
                       context=None):
        """
        The SummarizeNearby task finds features that are within a specified distance of features in the input layer. Distance can be measured as a straight-line distance, a drive-time distance (for example, within 10 minutes), or a drive distance (within 5 kilometers). Statistics are then calculated for the nearby features. For example:Calculate the total population within five minutes of driving time of a proposed new store location.Calculate the number of freeway access ramps within a one-mile driving distance of a proposed new store location to use as a measure of store accessibility.

        Parameters
        ----------
        sum_nearby_layer : Required layer (see Feature Input in documentation)
            Point, line, or polygon features from which distances will be measured to features in the summarizeLayer.
        summary_layer : Required layer (see Feature Input in documentation)
            Point, line, or polygon features. Features in this layer that are within the specified distance to features in the sumNearbyLayer will be summarized.
        near_type : Optional string
            Defines what kind of distance measurement you want to use to create areas around the nearbyLayer features. 
        distances : Required list of floats
            An array of double values that defines the search distance for creating areas mentioned above
        units : Optional string
            The linear unit for distances parameter above. Eg. Miles, Kilometers, Minutes Seconds etc
        time_of_day : Optional datetime.date
            For timeOfDay, set the time and day according to the number of milliseconds elapsed since the Unix epoc (January 1, 1970 UTC). When specified and if relevant for the nearType parameter, the traffic conditions during the time of the day will be considered.
        time_zone_for_time_of_day : Optional string
            Determines if the value specified for timeOfDay is specified in UTC or in a time zone that is local to the location of the origins. 
        return_boundaries : Optional bool
            If true, will return a result layer of areas that contain the requested summary information.  The resulting areas are defined by the specified nearType.  For example, if using a StraightLine of 5 miles, your result will contain areas with a 5 mile radius around the input features and specified summary information.If false, the resulting layer will return the same features as the input analysis layer with requested summary information. 
        sum_shape : Optional bool
            A boolean value that instructs the task to calculate count of points, length of lines or areas of polygons of the summaryLayer within each polygon in sumWithinLayer.
        shape_units : Optional string
            Specify units to summarize the length or areas when sumShape is set to true. Units is not required to summarize points.
        summary_fields : Optional list of strings
            A list of field names and statistical summary type that you wish to calculate for all features in the summaryLayer that are within each polygon in the sumWithinLayer . Eg: ["fieldname1 summary", "fieldname2 summary"]
        group_by_field : Optional string
            Specify a field from the summaryLayer features to calculate statistics separately for each unique value of the field.
        minority_majority : Optional bool
            This boolean parameter is applicable only when a groupByField is specified. If true, the minority (least dominant) or the majority (most dominant) attribute values within each group, within each boundary will be calculated.
        percent_shape : Optional bool
            This boolean parameter is applicable only when a groupByField is specified. If set to true, the percentage of shape (eg. length for lines) for each unique groupByField value is calculated.
        output_name : Optional string
            Additional properties such as output feature service name.
        context : Optional string
            Additional settings such as processing extent and output spatial reference.

        Returns
        -------
        dict with the following keys:
           "result_layer" : layer (FeatureCollection)
           "group_by_summary" : layer (FeatureCollection)
        """

        task ="SummarizeNearby"

        params = {}

        params["sumNearbyLayer"] = super()._feature_input(sum_nearby_layer)
        params["summaryLayer"] = super()._feature_input(summary_layer)
        if near_type is not None:
            params["nearType"] = near_type
        params["distances"] = distances
        if units is not None:
            params["units"] = units
        if time_of_day is not None:
            params["timeOfDay"] = time_of_day
        if time_zone_for_time_of_day is not None:
            params["timeZoneForTimeOfDay"] = time_zone_for_time_of_day
        if return_boundaries is not None:
            params["returnBoundaries"] = return_boundaries
        if sum_shape is not None:
            params["sumShape"] = sum_shape
        if shape_units is not None:
            params["shapeUnits"] = shape_units
        if summary_fields is not None:
            params["summaryFields"] = summary_fields
        if group_by_field is not None:
            params["groupByField"] = group_by_field
        if minority_majority is not None:
            params["minorityMajority"] = minority_majority
        if percent_shape is not None:
            params["percentShape"] = percent_shape
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['resultLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            
            result_layer = FeatureCollection(job_values['resultLayer'])

            group_by_summary = FeatureCollection(job_values['groupBySummary'])
            return { "result_layer":result_layer, "group_by_summary":group_by_summary, }


    def create_viewshed(self,
                       input_layer,
                       dem_resolution="Finest",
                       maximum_distance=None,
                       max_distance_units="Meters",
                       observer_height=None,
                       observer_height_units="Meters",
                       target_height=None,
                       target_height_units="Meters",
                       generalize=True,
                       output_name=None,
                       context=None):
        """
        

        Parameters
        ----------
        input_layer : Required layer (see Feature Input in documentation)
            
        dem_resolution : Optional string
            
        maximum_distance : Optional float
            
        max_distance_units : Optional string
            
        observer_height : Optional float
            
        observer_height_units : Optional string
            
        target_height : Optional float
            
        target_height_units : Optional string
            
        generalize : Optional bool
            
        output_name : Optional string
            
        context : Optional string
            

        Returns
        -------
        viewshed_layer : layer (FeatureCollection)
        """

        task ="CreateViewshed"

        params = {}

        params["inputLayer"] = super()._feature_input(input_layer)
        if dem_resolution is not None:
            params["demResolution"] = dem_resolution
        if maximum_distance is not None:
            params["maximumDistance"] = maximum_distance
        if max_distance_units is not None:
            params["maxDistanceUnits"] = max_distance_units
        if observer_height is not None:
            params["observerHeight"] = observer_height
        if observer_height_units is not None:
            params["observerHeightUnits"] = observer_height_units
        if target_height is not None:
            params["targetHeight"] = target_height
        if target_height_units is not None:
            params["targetHeightUnits"] = target_height_units
        if generalize is not None:
            params["generalize"] = generalize
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['viewshedLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['viewshedLayer'])


    def find_similar_locations(self,
                       input_layer,
                       search_layer,
                       analysis_fields=[],
                       input_query=None,
                       number_of_results=0,
                       output_name=None,
                       context=None):
        """
        

        Parameters
        ----------
        input_layer : Required layer (see Feature Input in documentation)
            
        search_layer : Required layer (see Feature Input in documentation)
            
        analysis_fields : Required list of strings
            
        input_query : Optional string
            
        number_of_results : Optional int
            
        output_name : Optional string
            
        context : Optional string
            

        Returns
        -------
        dict with the following keys:
           "similar_result_layer" : layer (FeatureCollection)
           "process_info" : layer (FeatureCollection)
        """

        task ="FindSimilarLocations"

        params = {}

        params["inputLayer"] = super()._feature_input(input_layer)
        params["searchLayer"] = super()._feature_input(search_layer)
        params["analysisFields"] = analysis_fields
        if input_query is not None:
            params["inputQuery"] = input_query
        if number_of_results is not None:
            params["numberOfResults"] = number_of_results
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['similarResultLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            
            similar_result_layer = FeatureCollection(job_values['similarResultLayer'])

            process_info = FeatureCollection(job_values['processInfo'])
            return { "similar_result_layer":similar_result_layer, "process_info":process_info, }


    def create_watersheds(self,
                       input_layer,
                       search_distance=None,
                       search_units="Meters",
                       source_database="FINEST",
                       generalize=True,
                       output_name=None,
                       context=None):
        """
        

        Parameters
        ----------
        input_layer : Required layer (see Feature Input in documentation)
            
        search_distance : Optional float
            
        search_units : Optional string
            
        source_database : Optional string
            
        generalize : Optional bool
            
        output_name : Optional string
            
        context : Optional string
            

        Returns
        -------
        dict with the following keys:
           "snap_pour_pts_layer" : layer (FeatureCollection)
           "watershed_layer" : layer (FeatureCollection)
        """

        task ="CreateWatersheds"

        params = {}

        params["inputLayer"] = super()._feature_input(input_layer)
        if search_distance is not None:
            params["searchDistance"] = search_distance
        if search_units is not None:
            params["searchUnits"] = search_units
        if source_database is not None:
            params["sourceDatabase"] = source_database
        if generalize is not None:
            params["generalize"] = generalize
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['snapPourPtsLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            
            snap_pour_pts_layer = FeatureCollection(job_values['snapPourPtsLayer'])

            watershed_layer = FeatureCollection(job_values['watershedLayer'])
            return { "snap_pour_pts_layer":snap_pour_pts_layer, "watershed_layer":watershed_layer, }


    def find_nearest(self,
                       analysis_layer,
                       near_layer,
                       measurement_type="StraightLine",
                       max_count=100,
                       search_cutoff=2147483647,
                       search_cutoff_units=None,
                       time_of_day=None,
                       time_zone_for_time_of_day="GeoLocal",
                       output_name=None,
                       context=None):
        """
        Measures the straight-line distance, driving distance, or driving time from features in the analysis layer to features in the near layer, and copies the nearest features in the near layer to a new layer. Returns a layer containing the nearest features and a line layer that links the start locations to their nearest locations.

        Parameters
        ----------
        analysis_layer : Required layer (see Feature Input in documentation)
            For each feature in this layer, the task finds the nearest features from the nearLayer.
        near_layer : Required layer (see Feature Input in documentation)
            The features from which the nearest locations are found.
        measurement_type : Required string
            The nearest locations can be determined by measuring straight-line distance, driving distance, or driving time
        max_count : Optional int
            The maximum number of near locations to find for each feature in analysisLayer.
        search_cutoff : Optional float
            Limits the search range to this value
        search_cutoff_units : Optional string
            The units for the value specified as searchCutoff
        time_of_day : Optional datetime.date
            When measurementType is DrivingTime, this value specifies the time of day to be used for driving time calculations based on traffic.
        time_zone_for_time_of_day : Optional string
            
        output_name : Optional string
            Additional properties such as output feature service name
        context : Optional string
            Additional settings such as processing extent and output spatial reference

        Returns
        -------
        dict with the following keys:
           "nearest_layer" : layer (FeatureCollection)
           "connecting_lines_layer" : layer (FeatureCollection)
        """

        task ="FindNearest"

        params = {}

        params["analysisLayer"] = super()._feature_input(analysis_layer)
        params["nearLayer"] = super()._feature_input(near_layer)
        params["measurementType"] = measurement_type
        if max_count is not None:
            params["maxCount"] = max_count
        if search_cutoff is not None:
            params["searchCutoff"] = search_cutoff
        if search_cutoff_units is not None:
            params["searchCutoffUnits"] = search_cutoff_units
        if time_of_day is not None:
            params["timeOfDay"] = time_of_day
        if time_zone_for_time_of_day is not None:
            params["timeZoneForTimeOfDay"] = time_zone_for_time_of_day
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['nearestLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            
            nearest_layer = FeatureCollection(job_values['nearestLayer'])

            connecting_lines_layer = FeatureCollection(job_values['connectingLinesLayer'])
            return { "nearest_layer":nearest_layer, "connecting_lines_layer":connecting_lines_layer, }


    def plan_routes(self,
                       stops_layer,
                       route_count,
                       max_stops_per_route,
                       route_start_time,
                       start_layer,
                       start_layer_route_id_field=None,
                       return_to_start=True,
                       end_layer=None,
                       end_layer_route_id_field=None,
                       travel_mode="Driving",
                       stop_service_time=0,
                       max_route_time=525600,
                       output_name=None,
                       context=None):
        """
        

        Parameters
        ----------
        stops_layer : Required layer (see Feature Input in documentation)
            
        route_count : Required int
            
        max_stops_per_route : Required int
            
        route_start_time : Required datetime.date
            
        start_layer : Required layer (see Feature Input in documentation)
            
        start_layer_route_id_field : Optional string
            
        return_to_start : Optional bool
            
        end_layer : Optional layer (see Feature Input in documentation)
            
        end_layer_route_id_field : Optional string
            
        travel_mode : Optional string
            
        stop_service_time : Optional float
            
        max_route_time : Optional float
            
        output_name : Optional string
            
        context : Optional string
            

        Returns
        -------
        dict with the following keys:
           "routes_layer" : layer (FeatureCollection)
           "assigned_stops_layer" : layer (FeatureCollection)
           "unassigned_stops_layer" : layer (FeatureCollection)
        """

        task ="PlanRoutes"

        params = {}

        params["stopsLayer"] = super()._feature_input(stops_layer)
        params["routeCount"] = route_count
        params["maxStopsPerRoute"] = max_stops_per_route
        params["routeStartTime"] = route_start_time
        params["startLayer"] = super()._feature_input(start_layer)
        if start_layer_route_id_field is not None:
            params["startLayerRouteIDField"] = start_layer_route_id_field
        if return_to_start is not None:
            params["returnToStart"] = return_to_start
        if end_layer is not None:
            params["endLayer"] = super()._feature_input(end_layer)
        if end_layer_route_id_field is not None:
            params["endLayerRouteIDField"] = end_layer_route_id_field
        if travel_mode is not None:
            params["travelMode"] = travel_mode
        if stop_service_time is not None:
            params["stopServiceTime"] = stop_service_time
        if max_route_time is not None:
            params["maxRouteTime"] = max_route_time
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['routesLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            
            routes_layer = FeatureCollection(job_values['routesLayer'])

            assigned_stops_layer = FeatureCollection(job_values['assignedStopsLayer'])

            unassigned_stops_layer = FeatureCollection(job_values['unassignedStopsLayer'])
            return { "routes_layer":routes_layer, "assigned_stops_layer":assigned_stops_layer, "unassigned_stops_layer":unassigned_stops_layer, }


    def trace_downstream(self,
                       input_layer,
                       split_distance=None,
                       split_units="Kilometers",
                       max_distance=None,
                       max_distance_units="Kilometers",
                       bounding_polygon_layer=None,
                       source_database=None,
                       generalize=True,
                       output_name=None,
                       context=None):
        """
        

        Parameters
        ----------
        input_layer : Required layer (see Feature Input in documentation)
            
        split_distance : Optional float
            
        split_units : Optional string
            
        max_distance : Optional float
            
        max_distance_units : Optional string
            
        bounding_polygon_layer : Optional layer (see Feature Input in documentation)
            
        source_database : Optional string
            
        generalize : Optional bool
            
        output_name : Optional string
            
        context : Optional string
            

        Returns
        -------
        trace_layer : layer (FeatureCollection)
        """

        task ="TraceDownstream"

        params = {}

        params["inputLayer"] = super()._feature_input(input_layer)
        if split_distance is not None:
            params["splitDistance"] = split_distance
        if split_units is not None:
            params["splitUnits"] = split_units
        if max_distance is not None:
            params["maxDistance"] = max_distance
        if max_distance_units is not None:
            params["maxDistanceUnits"] = max_distance_units
        if bounding_polygon_layer is not None:
            params["boundingPolygonLayer"] = super()._feature_input(bounding_polygon_layer)
        if source_database is not None:
            params["sourceDatabase"] = source_database
        if generalize is not None:
            params["generalize"] = generalize
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['traceLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return FeatureCollection(job_values['traceLayer'])


    def connect_origins_to_destinations(self,
                       origins_layer,
                       destinations_layer,
                       measurement_type="DrivingTime",
                       origins_layer_route_id_field=None,
                       destinations_layer_route_id_field=None,
                       time_of_day=None,
                       time_zone_for_time_of_day="GeoLocal",
                       output_name=None,
                       context=None):
        """
        Calculates routes between pairs of points.

        Parameters
        ----------
        origins_layer : Required layer (see Feature Input in documentation)
            The routes start from points in the origins layer.
        destinations_layer : Required layer (see Feature Input in documentation)
            The routes end at points in the destinations layer.
        measurement_type : Required string
            The routes can be determined by measuring travel distance or travel time along street network using different travel modes or by measuring straight line distance. 
        origins_layer_route_id_field : Optional string
            The field in the origins layer containing the IDs that are used to match an origin with a destination.
        destinations_layer_route_id_field : Optional string
            The field in the destinations layer containing the IDs that are used to match an origin with a destination.
        time_of_day : Optional datetime.date
            When measurementType is DrivingTime, this value specifies the time of day to be used for driving time calculations based on traffic. WalkingTime and TruckingTime measurementType do not support calculations based on traffic.
        time_zone_for_time_of_day : Optional string
            Determines if the value specified for timeOfDay is specified in UTC or in a time zone that is local to the location of the origins.
        output_name : Optional string
            Additional properties such as output feature service name.
        context : Optional string
            Additional settings such as processing extent and output spatial reference.

        Returns
        -------
        dict with the following keys:
           "routes_layer" : layer (FeatureCollection)
           "unassigned_origins_layer" : layer (FeatureCollection)
           "unassigned_destinations_layer" : layer (FeatureCollection)
        """

        task ="ConnectOriginsToDestinations"

        params = {}

        params["originsLayer"] = super()._feature_input(origins_layer)
        params["destinationsLayer"] = super()._feature_input(destinations_layer)
        params["measurementType"] = measurement_type
        if origins_layer_route_id_field is not None:
            params["originsLayerRouteIDField"] = origins_layer_route_id_field
        if destinations_layer_route_id_field is not None:
            params["destinationsLayerRouteIDField"] = destinations_layer_route_id_field
        if time_of_day is not None:
            params["timeOfDay"] = time_of_day
        if time_zone_for_time_of_day is not None:
            params["timeZoneForTimeOfDay"] = time_zone_for_time_of_day
        if output_name is not None:
            params["outputName"] = {"serviceProperties": {"name": output_name }}
        if context is not None:
            params["context"] = context

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['routesLayer']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            
            routes_layer = FeatureCollection(job_values['routesLayer'])

            unassigned_origins_layer = FeatureCollection(job_values['unassignedOriginsLayer'])

            unassigned_destinations_layer = FeatureCollection(job_values['unassignedDestinationsLayer'])
            return { "routes_layer":routes_layer, "unassigned_origins_layer":unassigned_origins_layer, "unassigned_destinations_layer":unassigned_destinations_layer, }

class RasterAnalysisTools(_AsyncService):
    "Represents the RasterAnalysisTools service. The RasterAnalysisTools service is used by ArcGIS Server to provide distributed raster analysis."

    def __init__(self, url, gis):
        """
        Constructs a client to the service given it's url from ArcGIS Online or Portal.
        """
        super().__init__(url, gis)
        self._gis = gis
        params = {
            "f" : "json"
        }

    def __str__(self):
        return json.dumps(self)

    


    def generate(self,
                       raster_function,
                       output_raster,
                       raster_arguments=None,
                       raster_properties=None,
                       context=None,
                       num_instances=None):
        """
        

        Parameters
        ----------
        raster_function : Required, see http://resources.arcgis.com/en/help/rest/apiref/israsterfunctions.html
            
        output_raster : Required string (output service + item name), or preexisting portal item
            
        raster_arguments : Optional string, for specifying input Raster alone, portal Item can be passed
            
        raster_properties : Optional 
            
        context : Optional 
            
        num_instances : Optional 
            

        Returns
        -------
        out_raster : image layer item, if none, one is created, can also pass string (name of item+service)
        """
        if output_raster is None:
            output_name = 'GeneratedRasterProduct' + '_' + _id_generator()
            output_raster = self._gis.content.create_service(output_name, "Service created by Copy Raster tool")
        elif isinstance(output_raster, str):
            try:
                matched = False
                items = self._gis.content.search(output_raster, max_items=6)
                for item in items:
                    if item is not None:
                        if output_raster == item['name']:
                            output_raster = { 'itemId' : item.itemid }
                            matched = True
                            break

                if not matched:
                    output_raster = self._gis.content.create_service(output_raster, "Service created by Copy Raster tool")
            except:
                output_raster = self._gis.content.create_service(output_raster, "Service created by Copy Raster tool")

        if isinstance(raster_arguments, arcgis.gis.Item):
            if raster_arguments.type.lower() == 'image service':
                raster_arguments =  { "Raster":{"itemId": raster_arguments.itemid } }
            else:
                raise TypeError("item type must be image service")

        task ="GenerateRaster"

        params = {}

        params["rasterFunction"] = raster_function
        params["outputRaster"] = super()._raster_input(output_raster)
        if raster_arguments is not None:
            params["rasterArguments"] = raster_arguments
        if raster_properties is not None:
            params["rasterProperties"] = raster_properties
        if context is not None:
            params["context"] = context
        if num_instances is not None:
            params["numInstances"] = num_instances

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        print(job_values)
        if output_raster is not None:
            itemid = job_values['outRaster']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            item.share(True)
            return item
        else:
            # Feature Collection
            return job_values['outRaster']


    def rasterize(self,
                       input_table,
                       output_raster,
                       raster_info,
                       value_field=None,
                       context=None,
                       num_instances=None):
        """
        

        Parameters
        ----------
        input_table : Required string
            
        output_raster : Required string
            
        raster_info : Required string
            
        value_field : Optional string
            
        context : Optional string
            
        num_instances : Optional string
            

        Returns
        -------
        out_raster : layer (FeatureCollection)
        """

        task ="Rasterize"

        params = {}

        params["inputTable"] = input_table
        params["outputRaster"] = output_raster
        params["rasterInfo"] = raster_info
        if value_field is not None:
            params["valueField"] = value_field
        if context is not None:
            params["context"] = context
        if num_instances is not None:
            params["numInstances"] = num_instances

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['outRaster']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return job_values['outRaster']


    def interpolate(self,
                       input_table,
                       output_raster,
                       raster_info,
                       value_field=None,
                       interpolation_method="Nearest",
                       radius=None,
                       context=None,
                       num_instances=None):
        """
        

        Parameters
        ----------
        input_table : Required string
            
        output_raster : Required string
            
        raster_info : Required string
            
        value_field : Optional string
            
        interpolation_method : Optional string
            
        radius : Optional float
            
        context : Optional string
            
        num_instances : Optional string
            

        Returns
        -------
        out_raster : layer (FeatureCollection)
        """

        task ="Interpolate"

        params = {}

        params["inputTable"] = input_table
        params["outputRaster"] = output_raster
        params["rasterInfo"] = raster_info
        if value_field is not None:
            params["valueField"] = value_field
        if interpolation_method is not None:
            params["interpolationMethod"] = interpolation_method
        if radius is not None:
            params["radius"] = radius
        if context is not None:
            params["context"] = context
        if num_instances is not None:
            params["numInstances"] = num_instances

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        #print(job_values)
        if output_name is not None:
            itemid = job_values['outRaster']['itemId']
            item = arcgis.gis.Item(self._portal, itemid)
            return item
        else:
            # Feature Collection
            return job_values['outRaster']


    def copy(self,
                       input_raster,
                       output_raster=None,
                       output_cellsize=None,
                       resampling_method="NEAREST",
                       clipping_geometry=None,
                       context=None,
                       num_instances=None):
        """
        

        Parameters
        ----------
        input_raster : Required string
            
        output_raster : Required string or image service item from portal. If string, specify name of the image service that will be created as output.
            
        output_cellsize : Optional dict, {"x": <numeric number>, "y": <numeric number>}
            
        resampling_method : Optional string, Values: Nearest | Bilinear | Cubic | Majority
            
        clipping_geometry : Optional dict, the JSON geometry object that is used to clip the input image. 
                            The clipping geometry object may contain the shape description, extent and the clip type. 

            
        context : Optional dict, eg { "outSR" : {spatial reference} }
            
        num_instances : Optional string
            

        Returns
        -------
        out_raster : layer (FeatureCollection)
        """

        task ="CopyRaster"
        
        if output_raster is None:
            output_name = input_raster['title'].replace (" ", "_") + '_' + 'Copy' + '_' + _id_generator()
            output_raster = self._gis.content.create_service(output_name, "Service created by Copy Raster tool")
        elif isinstance(output_raster, str):
            #check if there's an item by that name, if yes, use that
            try:
                item = self._gis.content.search(output_raster, max_items=1)[0]
                if item is not None:
                    if output_raster == item['name']:
                        output_raster = { 'itemid' : item['id'] }
                    else:
                        output_raster = self._gis.content.create_service(output_raster, "Service created by Copy Raster tool")
            except:
                output_raster = self._gis.content.create_service(output_raster, "Service created by Copy Raster tool")

        params = {}

        params["inputRaster"] = super()._raster_input(input_raster)
        params["outputRaster"] = super()._raster_input(output_raster)
        if output_cellsize is not None:
            params["outputCellsize"] = output_cellsize
        if resampling_method is not None:
            params["resamplingMethod"] = resampling_method
        if clipping_geometry is not None:
            params["clippingGeometry"] = clipping_geometry
        if context is not None:
            params["context"] = context
        if num_instances is not None:
            params["numInstances"] = num_instances

        task_url, job_info = super()._analysis_job(task, params)

        job_info = super()._analysis_job_status(task_url, job_info)
        job_values = super()._analysis_job_results(task_url, job_info)
        
        #print(job_values)
        
        itemid = job_values['outRaster']['itemId']
        item = arcgis.gis.Item(self._portal, itemid)
        item.share(True)
        return item
