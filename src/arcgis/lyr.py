"""
The arcgis.lyr module is used for accessing layers exposed from ArcGIS Online
or Portal.
"""
from __future__ import absolute_import
import arcgis.gis
import json
from pandas.io.json import json_normalize
import collections
from ._impl import *
from arcgis._impl.common._mixins import MutableAttr, AttrDict, AttrOrderedDict
import six
from arcgis._impl.service import _featureservice
from arcgis._impl.common import _utils
from arcgis._impl.common._spatial import *

class FeatureService(object):
    "represents a feature service"
    def __init__(self, item):
        """
        Constructs a Feature Service object given it's item from ArcGIS Online or Portal.
        """
        if item.type.lower() != 'feature service':
            raise TypeError("item type must be feature service")
        self.url = item.url
        self.item = item


        layers = []

        #print("URL of Feature Service: " + self.url)
        import re
        m = re.search(r'\d+$', self.url)
        # if the string ends in digits m will be a Match object, or None otherwise.
        if m is not None:
            layers.append(Layer(self.url, None, self.item))
        else:
            fsurl = self.url + '/layers'
            params = {
                "f" : "json"
            }

            allayers = self.item._portal.con.post(fsurl, params)
            try:
                for layer in allayers['layers']:
                    layers.append(Layer(self.url, layer, self.item))
                    #print("***" + str(layer))
                    #lyr_type = layer['type']
                    #lyr_url = self.url + '/' + str(layer['id'])
                    #layers.append({"type": lyr_type, "url" : lyr_url.replace(' ', '%20')})
            except:
                layers.append(Layer(self.url, allayers, self.item))

        #print(str(layers))
        self.layers = layers

    def __str__(self):
        return "Feature service at " + self.url

class Layer(object):
    """
    """
    
    def __init__(self, url, item, dictdata):
        """
        Constructs a service
        """
        self._portal = item._portal
        self.url = url
        self._url = url
        self._con = self._portal.con
        self.type = type(self).__name__
        self.properties = AttrOrderedDict(dictdata)

    def __str__(self):
        return '<%s url:"%s">' % (type(self).__name__, self.url)
    
    def __repr__(self):
        return '<%s url:"%s">' % (type(self).__name__, self.url)
    
    @property
    def _js_lyr(self):
        return { 'type' : type(self).__name__, 'url' : self.url }

class ImageLayer(Layer):
    def __init__(self, url, item, dictdata):
        super(ImageLayer, self).__init__(url, item, dictdata)

class FeatureLayer(Layer):
    def __init__(self, url, item, dictdata):
        super(FeatureLayer, self).__init__(url, item, dictdata)
        #self._obj = _featureservice.FeatureLayer(item=item, url=url,
        #                           initialize=False)
        if self.properties.hasAttachments:
            self.attachments = AttachmentManager(self)

    def _add_attachment(self, oid, file_path):
        """ Adds an attachment to a feature service
            Input:
              oid - string - OBJECTID value to add attachment to
              file_path - string - path to file
            Output:
              JSON Repsonse
        """
        if self.properties.hasAttachments:
            attachURL = self._url + "/%s/addAttachment" % oid
            params = {'f':'json'}

            files = {'attachment': file_path}
            res = self._con.post(path=attachURL,
                                 postdata=params,
                                 files=files)
            return res
        else:
            return "Attachments are not supported for this feature service."
    #----------------------------------------------------------------------
    def _delete_attachment(self, oid, attachment_id):
        """ removes an attachment from a feature service feature
            Input:
              oid - integer or string - id of feature
              attachment_id - integer - id of attachment to erase
            Output:
               JSON response
        """
        url = self._url + "/%s/deleteAttachments" % oid
        params = {
            "f":"json",
            "attachmentIds" : "%s" % attachment_id
        }
        return self._con.post(url, params)
    #----------------------------------------------------------------------
    def _update_attachment(self, oid, attachment_id, file_path):
        """ updates an existing attachment with a new file
            Inputs:
               oid - string/integer - Unique record ID
               attachment_id - integer - Unique attachment identifier
               file_path - string - path to new attachment
            Output:
               JSON response
        """
        url = self._url + "/%s/updateAttachment" % oid
        params = {
            "f":"json",
            "attachmentId" : "%s" % attachment_id
        }
        files = {'attachment': file_path }
        res = self._con.post(path=url,
                             postdata=params,
                             files=files)
        return res
    #----------------------------------------------------------------------
    def _list_attachments(self, oid):
        """ list attachements for a given OBJECT ID """
        url = self._url + "/%s/attachments" % oid
        params = {
            "f":"json"
        }
        return self._con.get(path=url, params=params)
    #----------------------------------------------------------------------
    def query(self,
              where="1=1",
              out_fields="*",
              timeFilter=None,
              geometryFilter=None,
              returnGeometry=True,
              returnCountOnly=False,
              returnIDsOnly=False,
              returnFeatureClass=False,
              returnDistinctValues=False,
              returnExtentOnly=False,
              groupByFieldsForStatistics=None,
              statisticFilter=None,
              resultOffset=None,
              resultRecordCount=None,
              out_fc=None,
              objectIds=None,
              distance=None,
              units=None,
              maxAllowableOffset=None,
              outSR=None,
              geometryPrecision=None,
              gdbVersion=None,
              orderByFields=None,
              outStatistics=None,
              returnZ=False,
              returnM=False,
              multipatchOption=None,
              quanitizationParameters=None,
              returnCentroid=False,
              as_json=False,
              **kwargs):
        """ queries a feature service based on a sql statement
            Inputs:
                where - the selection sql statement
                out_fields - the attribute fields to return
                objectIds -  The object IDs of this layer or table to be
                            queried.
                distance - The buffer distance for the input geometries.
                          The distance unit is specified by units. For
                          example, if the distance is 100, the query
                          geometry is a point, units is set to meters, and
                          all points within 100 meters of the point are
                          returned.
                units - The unit for calculating the buffer distance. If
                        unit is not specified, the unit is derived from the
                        geometry spatial reference. If the geometry spatial
                        reference is not specified, the unit is derived
                        from the feature service data spatial reference.
                        This parameter only applies if
                        supportsQueryWithDistance is true.
                        Values: esriSRUnit_Meter | esriSRUnit_StatuteMile |
                        esriSRUnit_Foot | esriSRUnit_Kilometer |
                        esriSRUnit_NauticalMile | esriSRUnit_USNauticalMile
                timeFilter - a TimeFilter object where either the start time
                            or start and end time are defined to limit the
                            search results for a given time.  The values in
                            the timeFilter should be as UTC timestampes in
                            milliseconds.  No checking occurs to see if they
                            are in the right format.
                geometryFilter - a GeometryFilter object to parse down a given
                               query by another spatial dataset.
                maxAllowableOffset - This option can be used to specify the
                                     maxAllowableOffset to be used for
                                     generalizing geometries returned by
                                     the query operation.
                                     The maxAllowableOffset is in the units
                                     of outSR. If outSR is not specified,
                                     maxAllowableOffset is assumed to be in
                                     the unit of the spatial reference of
                                     the map.
                outSR - The spatial reference of the returned geometry.
                geometryPrecision -  This option can be used to specify the
                                     number of decimal places in the
                                     response geometries returned by the
                                     Query operation.
                gdbVersion - Geodatabase version to query
                returnDistinctValues -  If true, it returns distinct values
                                        based on the fields specified in
                                        outFields. This parameter applies
                                        only if the
                                        supportsAdvancedQueries property of
                                        the layer is true.
                returnIDsOnly -  If true, the response only includes an
                                 array of object IDs. Otherwise, the
                                 response is a feature set. The default is
                                 false.
                returnCountOnly -  If true, the response only includes the
                                   count (number of features/records) that
                                   would be returned by a query. Otherwise,
                                   the response is a feature set. The
                                   default is false. This option supersedes
                                   the returnIdsOnly parameter. If
                                   returnCountOnly = true, the response will
                                   return both the count and the extent.
                returnExtentOnly -  If true, the response only includes the
                                    extent of the features that would be
                                    returned by the query. If
                                    returnCountOnly=true, the response will
                                    return both the count and the extent.
                                    The default is false. This parameter
                                    applies only if the
                                    supportsReturningQueryExtent property
                                    of the layer is true.
                orderByFields - One or more field names on which the
                                features/records need to be ordered. Use
                                ASC or DESC for ascending or descending,
                                respectively, following every field to
                                control the ordering.
                groupByFieldsForStatistics - One or more field names on
                                             which the values need to be
                                             grouped for calculating the
                                             statistics.
                outStatistics - The definitions for one or more field-based
                                statistics to be calculated.
                returnZ -  If true, Z values are included in the results if
                           the features have Z values. Otherwise, Z values
                           are not returned. The default is false.
                returnM - If true, M values are included in the results if
                          the features have M values. Otherwise, M values
                          are not returned. The default is false.
                multipatchOption - This option dictates how the geometry of
                                   a multipatch feature will be returned.
                resultOffset -  This option can be used for fetching query
                                results by skipping the specified number of
                                records and starting from the next record
                                (that is, resultOffset + 1th).
                resultRecordCount - This option can be used for fetching
                                    query results up to the
                                    resultRecordCount specified. When
                                    resultOffset is specified but this
                                    parameter is not, the map service
                                    defaults it to maxRecordCount. The
                                    maximum value for this parameter is the
                                    value of the layer's maxRecordCount
                                    property.
                quanitizationParameters - Used to project the geometry onto
                                          a virtual grid, likely
                                          representing pixels on the screen.
                returnCentroid - Used to return the geometry centroid
                                 associated with each feature returned. If
                                 true, the result includes the geometry
                                 centroid. The default is false.
                as_json - If true, the query will return as the raw JSON.
                          The default is False.
                returnFeatureClass - If true and arcpy is installed, the
                                     script will attempt to save the result
                                     of the query to a feature class.
                out_fc - only valid if returnFeatureClass is set to True.
                         Output location of query. If out_fc is set to None,
                         then the feature class will be saved to the scratch
                         File Geodatabase with a random name.
               kwargs - optional parameters that can be passed to the Query
                 function.  This will allow users to pass additional
                 parameters not explicitly implemented on the function. A
                 complete list of functions available is documented on the
                 Query REST API.
            Output:
               A list of Feature Objects (default) or a path to the output featureclass if
               returnFeatureClass is set to True.
         """
        url = self._url + "/query"
        params = {"f" : "json"}
        params['where'] = where
        params['outFields'] = out_fields
        params['returnGeometry'] = returnGeometry
        params['returnDistinctValues'] = returnDistinctValues
        params['returnCentroid'] = returnCentroid
        params['returnCountOnly'] = returnCountOnly
        params['returnExtentOnly'] = returnExtentOnly
        params['returnIdsOnly'] = returnIDsOnly
        params['returnZ'] = returnZ
        params['returnM'] = returnM
        if resultRecordCount:
            params['resultRecordCount'] = resultRecordCount
        if resultOffset:
            params['resultOffset'] = resultOffset
        if quanitizationParameters:
            params['quanitizationParameters'] = quanitizationParameters
        if multipatchOption:
            params['multipatchOption'] = multipatchOption
        if orderByFields:
            params['orderByFields'] = orderByFields
        if groupByFieldsForStatistics:
            params['groupByFieldsForStatistics'] = groupByFieldsForStatistics
        if statisticFilter and \
           isinstance(statisticFilter, StatisticFilter):
            params['outStatistics'] = statisticFilter.filter
        if outStatistics:
            params['outStatistics'] = outStatistics
        if outSR:
            params['outSR'] = outSR
        if maxAllowableOffset:
            params['maxAllowableOffset'] = maxAllowableOffset
        if gdbVersion:
            params['gdbVersion'] = gdbVersion
        if geometryPrecision:
            params['geometryPrecision'] = geometryPrecision
        if objectIds:
            params['objectIds'] = objectIds
        if distance:
            params['distance'] = distance
        if units:
            params['units'] = units
        if timeFilter and \
           isinstance(timeFilter, TimeFilter):
            for k,v in timeFilter.filter:
                params[k] = v
        elif isinstance(timeFilter, dict):
            for k,v in timeFilter.items():
                params[k] = v
        if geomtryFilter and \
           isinstance(geomtryFilter, GeometryFilter):
            for k,v in geomtryFilter.filter:
                params[k] = v
        elif geomtryFilter and \
             isinstance(geomtryFilter, dict):
            for k,v in geomtryFilter.items():
                params[k] = v
        if len(kwargs) > 0:
            for k,v in kwargs.items():
                params[k] = v
                del k,v

        result = self._con.post(path=url,
                                postdata=params)
        if 'error' in result:
            raise ValueError(result)
        
        if  returnCountOnly:
            return result['count']
        elif as_json or returnIDsOnly:
            return result
        elif returnFeatureClass and \
             not returnCountOnly and \
             not returnIDsOnly:
            uid = _utils.create_uid()
            if out_fc is None:
                out_fc = os.path.join(scratchGDB(),
                                      "a{fid}".format(fid=uid))
            text = json.dumps(result)
            temp = scratchFolder() + os.sep + uid + ".json"
            with open(temp, 'wb') as writer:
                if six.PY3:
                        text = bytes(text, 'UTF-8')
                writer.write(text)
                writer.flush()
                del writer
            fc = json_to_featureclass(json_file=temp,
                                      out_fc=out_fc)
            os.remove(temp)
            return fc
        else:
            df = json_normalize(result['features'])
            df.columns = df.columns.str.replace('attributes.', '')
            return df
            #return FeatureSet.fromJSON(jsonValue=json.dumps(result))
        return result
    #----------------------------------------------------------------------
    def query_related_records(self,
                              objectIds,
                              relationshipId,
                              outFields="*",
                              definitionExpression=None,
                              returnGeometry=True,
                              maxAllowableOffset=None,
                              geometryPrecision=None,
                              outWKID=None,
                              gdbVersion=None,
                              returnZ=False,
                              returnM=False):
        """
           The Query operation is performed on a feature service layer
           resource. The result of this operation are feature sets grouped
           by source layer/table object IDs. Each feature set contains
           Feature objects including the values for the fields requested by
           the user. For related layers, if you request geometry
           information, the geometry of each feature is also returned in
           the feature set. For related tables, the feature set does not
           include geometries.
           Inputs:
              objectIds - the object IDs of the table/layer to be queried
              relationshipId - The ID of the relationship to be queried.
              outFields - the list of fields from the related table/layer
                          to be included in the returned feature set. This
                          list is a comma delimited list of field names. If
                          you specify the shape field in the list of return
                          fields, it is ignored. To request geometry, set
                          returnGeometry to true.
                          You can also specify the wildcard "*" as the
                          value of this parameter. In this case, the result
                          s will include all the field values.
              definitionExpression - The definition expression to be
                                     applied to the related table/layer.
                                     From the list of objectIds, only those
                                     records that conform to this
                                     expression are queried for related
                                     records.
              returnGeometry - If true, the feature set includes the
                               geometry associated with each feature. The
                               default is true.
              maxAllowableOffset - This option can be used to specify the
                                   maxAllowableOffset to be used for
                                   generalizing geometries returned by the
                                   query operation. The maxAllowableOffset
                                   is in the units of the outSR. If outSR
                                   is not specified, then
                                   maxAllowableOffset is assumed to be in
                                   the unit of the spatial reference of the
                                   map.
              geometryPrecision - This option can be used to specify the
                                  number of decimal places in the response
                                  geometries.
              outWKID - The spatial reference of the returned geometry.
              gdbVersion - The geodatabase version to query. This parameter
                           applies only if the isDataVersioned property of
                           the layer queried is true.
              returnZ - If true, Z values are included in the results if
                        the features have Z values. Otherwise, Z values are
                        not returned. The default is false.
              returnM - If true, M values are included in the results if
                        the features have M values. Otherwise, M values are
                        not returned. The default is false.
        """
        params = {
            "f" : "json",
            "objectIds" : objectIds,
            "relationshipId" : relationshipId,
            "outFields" : outFields,
            "returnGeometry" : returnGeometry,
            "returnM" : returnM,
            "returnZ" : returnZ
        }
        if gdbVersion is not None:
            params['gdbVersion'] = gdbVersion
        if definitionExpression is not None:
            params['definitionExpression'] = definitionExpression
        if outWKID is not None and \
           isinstance(outWKID, SpatialReference):
            params['outSR'] = outWKID
        elif outWKID is not None and \
             isinstance(outWKID, dict):
            params['outSR'] = outWKID
        if maxAllowableOffset is not None:
            params['maxAllowableOffset'] = maxAllowableOffset
        if geometryPrecision is not None:
            params['geometryPrecision'] = geometryPrecision
        quURL = self._url + "/queryRelatedRecords"
        return self._con.get(path=quURL, params=params)
    #----------------------------------------------------------------------
    def get_html_popup(self, oid):
        """
           The htmlPopup resource provides details about the HTML pop-up
           authored by the user using ArcGIS for Desktop.
           Input:
              oid - object id of the feature where the HTML pop-up
           Output:

        """
        if hasattr(self, "htmlPopupType") and \
           getattr(self, "htmlPopupType") != "esriServerHTMLPopupTypeNone":
            popURL = self._url + "/%s/htmlPopup" % oid
            params = {
                'f' : "json"
            }

            return self._con.get(path=popURL, params=params)
        return ""
    #----------------------------------------------------------------------
    def edit_features(self,
                   adds=None,
                   updates=None,
                   deletes=None,
                   gdbVersion=None,
                   useGlobalIds=False,
                   rollbackOnFailure=True):
        """
           This operation adds, updates, and deletes features to the
           associated feature layer or table in a single call.
           Inputs:
              adds - The array of features to be added.  These
                            features should be common.Feature objects
              updates - The array of features to be updateded.
                               These features should be common.Feature
                               objects
              deletes - string of OIDs to remove from service
              gdbVersion - Geodatabase version to apply the edits.
              useGlobalIds - instead of referencing the default Object ID
                              field, the service will look at a GUID field
                              to track changes.  This means the GUIDs will
                              be passed instead of OIDs for delete,
                              update or add features.
              rollbackOnFailure - Optional parameter to specify if the
                                  edits should be applied only if all
                                  submitted edits succeed. If false, the
                                  server will apply the edits that succeed
                                  even if some of the submitted edits fail.
                                  If true, the server will apply the edits
                                  only if all edits succeed. The default
                                  value is true.
           Output:
              dictionary of messages
        """
        if adds is None:
            adds = []
        if updates is None:
            updates = []
        editURL = self._url + "/applyEdits"
        params = {"f": "json",
                  "useGlobalIds" : useGlobalIds,
                  "rollbackOnFailure" : rollbackOnFailure
                  }
        if gdbVersion is not None:
            params['gdbVersion'] = gdbVersion
        if len(adds) > 0 and \
           isinstance(adds[0], dict):
            params['adds'] = json.dumps([f for f in adds],
                                        default=_date_handler)
        if len(updates) > 0 and \
           isinstance(updates[0], dict):
            params['updates'] = json.dumps([f for f in updates],
                                           default=_date_handler)
        if deletes is not None and \
           isinstance(deletes, str):
            params['deletes'] = deletes
        return self._con.post(path=editURL, postdata=params)
    #----------------------------------------------------------------------
    def calculate(self, where, calc_expression, sql_format="standard"):
        """
        The calculate operation is performed on a feature service layer
        resource. It updates the values of one or more fields in an
        existing feature service layer based on SQL expressions or scalar
        values. The calculate operation can only be used if the
        supportsCalculate property of the layer is true.
        Neither the Shape field nor system fields can be updated using
        calculate. System fields include ObjectId and GlobalId.
        See Calculate a field for more information on supported expressions

        Inputs:
           where - A where clause can be used to limit the updated records.
                   Any legal SQL where clause operating on the fields in
                   the layer is allowed.
           calcExpression - The array of field/value info objects that
                            contain the field or fields to update and their
                            scalar values or SQL expression.  Allowed types
                            are dictionary and list.  List must be a list
                            of dictionary objects.
                            Calculation Format is as follows:
                               {"field" : "<field name>",
                               "value" : "<value>"}
           sqlFormat - The SQL format for the calcExpression. It can be
                       either standard SQL92 (standard) or native SQL
                       (native). The default is standard.
                       Values: standard, native
        Output:
           JSON as string
        Usage:
        >>>sh = arcrest.AGOLTokenSecurityHandler("user", "pw")
        >>>fl = arcrest.agol.FeatureLayer(url="someurl",
                                     securityHandler=sh, initialize=True)
        >>>print fl.calculate(where="OBJECTID < 2",
                              calcExpression={"field": "ZONE",
                                              "value" : "R1"})
        {'updatedFeatureCount': 1, 'success': True}
        """
        url = self._url + "/calculate"
        params = {
            "f" : "json",
            "where" : where,

        }
        if isinstance(calc_expression, dict):
            params["calcExpression"] = json.dumps([calc_expression],
                                                  default=_date_handler)
        elif isinstance(calc_expression, list):
            params["calcExpression"] = json.dumps(calc_expression,
                                                  default=_date_handler)
        if sql_format.lower() in ['native', 'standard']:
            params['sqlFormat'] = sql_format.lower()
        else:
            params['sqlFormat'] = "standard"
        return self._con.post(path=url,
                              postdata=params)

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
        return self._layer._con.get(path=att_path, try_json=False, out_folder=save_path)

    def add(self, oid, file_path):
        """ Adds an attachment to a feature service
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

class FeatureCollection(Layer):
    """
    """
    def __init__(self, url, item, dictdata):
        super(FeatureCollection, self).__init__(url, item, dictdata)

    @property
    def _js_lyr(self):
        return self.properties

    def query(self):
        """Returns the data in this feature collection as a pandas data frame. Filtering by SQL statement is not supported for feature collections.
        """
        if 'layers' in self.properties:
            df = json_normalize(self.properties['layers'][0]['featureSet']['features'])
        else:
            df = json_normalize(self.properties['featureSet']['features'])

        df.columns = df.columns.str.replace('attributes.', '')
        return df
    
class Service(object):
    """
    """
    def __init__(self, svcurl, gis=None, dictdata=None):
        """
        Constructs a service
        """
        if dictdata is None:
            self._con = gis._portal.con
            params = {"f": "json"}
            dictdata = self._con.post(svcurl, params, use_ordered_dict=True)
        
        self.url = svcurl

        if gis is None:
            gis = GIS()
                    
        self.definition = AttrOrderedDict(dictdata)

    def __str__(self):
        return json.dumps(self)

    def query(self,
              where="1=1",
              out_fields="*",
              timeFilter=None,
              geometryFilter=None,
              returnGeometry=True,
              returnIDsOnly=False,
              returnCountOnly=False,
              returnFeatureClass=False,
              returnDistinctValues=False,
              returnExtentOnly=False,
              groupByFieldsForStatistics=None,
              statisticFilter=None,
              out_fc=None,
              objectIds="",
              **kwargs):
        """ queries a feature service based on a sql statement
            Inputs:
               where - the selection sql statement
               out_fields - the attribute fields to return
               timeFilter - a TimeFilter object where either the start time
                            or start and end time are defined to limit the
                            search results for a given time.  The values in
                            the timeFilter should be as UTC timestampes in
                            milliseconds.  No checking occurs to see if they
                            are in the right format.
               geometryFilter - a GeometryFilter object to parse down a given
                               query by another spatial dataset.
               returnGeometry - true means a geometry will be returned,
                                else just the attributes
               returnIDsOnly - false is default.  True means only OBJECTIDs
                               will be returned
               returnCountOnly - if True, then an integer is returned only
                                 based on the sql statement
               returnFeatureClass - Default False. If true, query will be
                                    returned as feature class
               groupByFieldsForStatistics - One or more field names on
                                    which the values need to be grouped for
                                    calculating the statistics.
               statisticFilter - object that performs statistic queries
               out_fc - only valid if returnFeatureClass is set to True.
                        Output location of query.
               kwargs - optional parameters that can be passed to the Query
                 function.  This will allow users to pass additional
                 parameters not explicitly implemented on the function. A
                 complete list of functions available is documented on the
                 Query REST API.
            Output:
               A list of Feature Objects (default) or a path to the output featureclass if
               returnFeatureClass is set to True.
         """
        params = {"f": "json",
                  "where": where,
                  "outFields": out_fields,
                  "returnGeometry" : returnGeometry,
                  "returnIdsOnly" : returnIDsOnly,
                  "returnCountOnly" : returnCountOnly,
                  "returnDistinctValues" : returnDistinctValues,
                  "returnExtentOnly" : returnExtentOnly
                  }
        for key, value in kwargs.items():
            params[key] = value
        if not timeFilter is None and \
           isinstance(timeFilter, filters.TimeFilter):
            params['time'] = timeFilter.filter
        if not geometryFilter is None and \
           isinstance(geometryFilter, filters.GeometryFilter):
            gf = geometryFilter.filter
            params['geometry'] = gf['geometry']
            params['geometryType'] = gf['geometryType']
            params['spatialRelationship'] = gf['spatialRel']
            params['inSR'] = gf['inSR']
        if objectIds is not None and objectIds != "":
            params['objectIds'] = objectIds
        if not groupByFieldsForStatistics is None:
            params['groupByFieldsForStatistics'] = groupByFieldsForStatistics
        if not statisticFilter is None and \
           isinstance(statisticFilter, filters.StatisticFilter):
            params['outStatistics'] = statisticFilter.filter
        fURL = self.url + "/query"
        #print(fURL)
        results = self._con.post(fURL, params)

        if 'error' in results:
            raise ValueError (results)
        if not returnCountOnly and not returnIDsOnly:
            if returnFeatureClass == True:
                #json_text = json.dumps(results)
                #return results
                df = json_normalize(results['features'])
                df.columns = df.columns.str.replace('attributes.', '')
                return df
            else:
                #return results #FeatureSet.fromJSON(json.dumps(results))
                #print(results)
                df = json_normalize(results['features'])
                df.columns = df.columns.str.replace('attributes.', '')
                return df
        else:
            return results
        return




