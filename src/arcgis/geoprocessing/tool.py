
import collections
import datetime
import inspect
import json
import re
import time
import types
import tempfile

import arcgis.env
from ..features import FeatureSet, FeatureCollection, FeatureLayerCollection
from ..gis import _GISResource, Item, Layer
from .._impl.common._mixins import PropertyMap
from .._impl.common._utils import _date_handler


def _camelCase_to_underscore(name):
    """PEP8ify name"""
    if '_' in name:
        return name.lower()
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class LinearUnit(object):
    """
    A data object containing a linear distance, used as input to some Geoprocessing tools

        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        distance          required number, the value of the linear distance.

        ----------------  --------------------------------------------------------
        units             required string,  unit type of the linear distance,
                          such as "Meters", "Miles", "Kilometers" etc.
        ================  ========================================================
    """
    def __init__(self, distance, units):
        self.distance = distance
        if units.startswith('esri'):
            self.units = units
        else:
            self.units = 'esri' + units

    def to_dict(self):
        return {"distance": self.distance, "units": self.units}

    def __repr__(self):
        return '<%s "%d %s">' % (type(self).__name__, self.distance, self.units)

    def __str__(self):
        return '<%s "%d %s">' % (type(self).__name__, self.distance, self.units)

    @classmethod
    def from_dict(cls, datadict):
        """Creates an instance of this class from its dict representation."""
        distance = datadict.get('distance', None)
        units = datadict.get('units', None)

        return cls(distance, units)


class DataFile(object):
    """
    A data object containing a data source, used as input/output by some Geoprocessing tools

        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        url               optional string, URL to the location of the data file.

        ----------------  --------------------------------------------------------
        item_id           optional string,  The id of the uploaded file returned
                          as a result of the upload operation.
        ================  ========================================================
    """
    def __init__(self, url=None, item_id=None):
        self.url = url
        self.item_id = item_id

    def to_dict(self):
        datafile = {}
        if self.url is not None:
            datafile['url'] = self.url
        if self.item_id is not None:
            datafile['itemID'] = self.item_id
        return datafile

    def __repr__(self):
        return '<%s "%s">' % (type(self).__name__, self.to_dict())

    def __str__(self):
        return '<%s "%s">' % (type(self).__name__, self.to_dict())


    @classmethod
    def from_dict(cls, datadict):
        """Creates an instance of this class from its dict representation."""
        url = datadict.get('url', None)
        item_id = datadict.get('item_id', None)

        return cls(url, item_id)


    def download(self, save_path=None):
        """Downloads the data to the specified folder or a tempoary folder if a folder isn't provided"""
        data_path = self.url
        if not save_path:
            save_path = tempfile.gettempdir()
        if data_path:
            filename = data_path.split('/')[-1]
            return self._con.get(path=data_path, file_name=filename,
                                        out_folder=save_path, try_json=False, token=self._token)


class RasterData(object):
    """
    A data object containing a raster data source,
    used as input/output by some Geoprocessing tools

        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        url               optional string, URL to the location of the raster data
                          file.
        ----------------  --------------------------------------------------------
        item_id           optional string,  The id of the uploaded file returned
                          as a result of the upload operation.
        ----------------  --------------------------------------------------------
        format            optional string, Specifies the format of the raster
                          data, such as "jpg", "tif", etc.
        ================  ========================================================
    """
    def __init__(self, url=None, format=None, item_id=None):
        self.url = url
        self.format = format
        self.item_id = item_id

    def to_dict(self):
        """Converts an instance of this class to its dict representation."""
        rasterdata = {}
        if self.url is not None:
            rasterdata['url'] = self.url
        if self.item_id is not None:
            rasterdata['itemID'] = self.item_id
        if self.format is not None:
            rasterdata['format'] = self.format

        return rasterdata

    def __repr__(self):
        return '<%s "%s">' % (type(self).__name__, self.to_dict())

    def __str__(self):
        return '<%s "%s">' % (type(self).__name__, self.to_dict())

    @classmethod
    def from_dict(cls, datadict):
        """Creates an instance of this class from its dict representation."""
        url = datadict.get('url', None)
        item_id = datadict.get('item_id', None)
        format = datadict.get('format', None)

        return cls(url, format, item_id)


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
                              _camelCase_to_underscore(fnname),
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


class _AsyncResource(_GISResource):
    def __init__(self, url, gis):
        super(_AsyncResource, self).__init__(url, gis)

    def _refresh(self):
        params = {"f": "json"}
        dictdata = self._con.get(path=self.url, params=params, token=self._token)
        self.properties = PropertyMap(dictdata)

    def _analysis_job(self, task, params):
        """ Submits an Analysis job and returns the job URL for monitoring the job
            status in addition to the json response data for the submitted job."""

        # Unpack the Analysis job parameters as a dictionary and add token and
        # formatting parameters to the dictionary. The dictionary is used in the
        # HTTP POST request. Headers are also added as a dictionary to be included
        # with the POST.
        #
        # print("Submitting analysis job...")

        task_url = "{}/{}".format(self.url, task)
        submit_url = "{}/submitJob".format(task_url)

        params["f"] = "json"

        resp = self._con.post(submit_url, params, token=self._token)
        # print(resp)
        return task_url, resp

    def _analysis_job_status(self, task_url, job_info):
        """ Tracks the status of the submitted Analysis job."""

        if "jobId" in job_info:
            # Get the id of the Analysis job to track the status.
            #
            job_id = job_info.get("jobId")
            job_url = "{}/jobs/{}".format(task_url, job_id)
            params = {"f": "json"}
            job_response = self._con.post(job_url, params, token=self._token)

            # Query and report the Analysis job status.
            #
            num_messages = 0

            if "jobStatus" in job_response:
                while not job_response.get("jobStatus") == "esriJobSucceeded":
                    time.sleep(5)

                    job_response = self._con.post(job_url, params, token=self._token)
                    # print(job_response)
                    messages = job_response['messages'] if 'messages' in job_response else []
                    num = len(messages)
                    if num > num_messages:
                        for index in range(num_messages, num):
                            msg = messages[index]
                            if msg['type'] == 'esriJobMessageTypeInformative':
                                print(msg['description'])
                            else:
                                print(msg['description'])  # ,file = sys.stderr)
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

                        params = {"f": "json"}
                        param_result = self._con.post(result_url, params, token=self._token)

                        job_value = param_result.get("value")
                        result_values[key] = job_value
                return result_values
            else:
                raise Exception("Unable to get analysis job results.")
        else:
            raise Exception("Unable to get analysis job results.")

    def _feature_input(self, input_layer):

        point_fs = {
            "layerDefinition": {
                "currentVersion": 10.11,
                "copyrightText": "",
                "defaultVisibility": True,
                "relationships": [

                ],
                "isDataVersioned": False,
                "supportsRollbackOnFailureParameter": True,
                "supportsStatistics": True,
                "supportsAdvancedQueries": True,
                "geometryType": "esriGeometryPoint",
                "minScale": 0,
                "maxScale": 0,
                "objectIdField": "OBJECTID",
                "templates": [

                ],
                "type": "Feature Layer",
                "displayField": "TITLE",
                "visibilityField": "VISIBLE",
                "name": "startDrawPoint",
                "hasAttachments": False,
                "typeIdField": "TYPEID",
                "capabilities": "Query",
                "allowGeometryUpdates": True,
                "htmlPopupType": "",
                "hasM": False,
                "hasZ": False,
                "globalIdField": "",
                "supportedQueryFormats": "JSON",
                "hasStaticData": False,
                "maxRecordCount": -1,
                "indexes": [

                ],
                "types": [

                ],
                "fields": [
                    {
                        "alias": "OBJECTID",
                        "name": "OBJECTID",
                        "type": "esriFieldTypeOID",
                        "editable": False
                    },
                    {
                        "alias": "Title",
                        "name": "TITLE",
                        "length": 50,
                        "type": "esriFieldTypeString",
                        "editable": True
                    },
                    {
                        "alias": "Visible",
                        "name": "VISIBLE",
                        "type": "esriFieldTypeInteger",
                        "editable": True
                    },
                    {
                        "alias": "Description",
                        "name": "DESCRIPTION",
                        "length": 1073741822,
                        "type": "esriFieldTypeString",
                        "editable": True
                    },
                    {
                        "alias": "Type ID",
                        "name": "TYPEID",
                        "type": "esriFieldTypeInteger",
                        "editable": True
                    }
                ]
            },
            "featureSet": {
                "features": [
                    {
                        "geometry": {
                            "x": 80.27032792000051,
                            "y": 13.085227147000467,
                            "spatialReference": {
                                "wkid": 4326,
                                "latestWkid": 4326
                            }
                        },
                        "attributes": {
                            "description": "blayer desc",
                            "title": "blayer",
                            "OBJECTID": 0,
                            "VISIBLE": 1
                        },
                        "symbol": {
                            "angle": 0,
                            "xoffset": 0,
                            "yoffset": 8.15625,
                            "type": "esriPMS",
                            "url": "https://cdn.arcgis.com/cdn/7674/js/jsapi/esri/dijit/images/Directions/greenPoint.png",
                            "imageData": "iVBORw0KGgoAAAANSUhEUgAAABUAAAAdCAYAAABFRCf7AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyRpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMC1jMDYxIDY0LjE0MDk0OSwgMjAxMC8xMi8wNy0xMDo1NzowMSAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNS4xIE1hY2ludG9zaCIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDo4OTI1MkU2ODE0QzUxMUUyQURFMUNDNThGMTA3MjkzMSIgeG1wTU06RG9jdW1lbnRJRD0ieG1wLmRpZDo4OTI1MkU2OTE0QzUxMUUyQURFMUNDNThGMTA3MjkzMSI+IDx4bXBNTTpEZXJpdmVkRnJvbSBzdFJlZjppbnN0YW5jZUlEPSJ4bXAuaWlkOjg5MjUyRTY2MTRDNTExRTJBREUxQ0M1OEYxMDcyOTMxIiBzdFJlZjpkb2N1bWVudElEPSJ4bXAuZGlkOjg5MjUyRTY3MTRDNTExRTJBREUxQ0M1OEYxMDcyOTMxIi8+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwveDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+iVNkdQAABJlJREFUeNp0VltvG0UUnpkdr72261CnCQWEIA9FqOKlqooARUKCtAUhoA+VoBVRhfgFXKSKJ97goRL8ARCIclGgL0VUkBBAoBaVoggEQQVSAhFS06SJje3Y3t25cc7srL3YjddHs3N85pvvfOfMyJRs83n8o+P7POI9yQibooTeBa68ISbSRv+hifpCGHX2s6dnfrrRWjroOPzB0T0+zZ0q8uDRSrniF/MB8X2fADhR8IRRRDphh7Q6rbgtOucU0Sdnj59Z2hb00PtHD+Zp/p2x6uitO4o7iLYP8DMafjVE2wXUboALm50W2ahtXO3q8MTX02fnh0Affu/IkSAXnL55dLzMPU6kURZMIZQhFtRk2VBKcpQTIQVZ21hrdUX4zDcnPv2kBzr59mP3BLnChfGx8YrHPKIAELSzMPhQk+ydzpOvIYwywjFeK7K+vt6IlZw8/+y5RZ4gm9eCUrGCmkUyBkCV0Sd5UlBtTLIhRWQE9ixwsVwe6dY3X4WwJ+j9bx7a7/v5i6O7qlxisFZJAvBF7Rjty56CWlmszilj6BNgXd+syTCO7uNK62nuezyUkWWASTPHDtOjbgOHkJTOsbXAyJhIC+rlODdROM211gcQKBJxoh+EKAs4AGqybHVfBvdICNIU/IDHYbcJiS6le4wwbW1B9UDXJcg9QBxtbglh1BlAJzjoUxIGQZFRwtAypgnjtH0spDG9MWVs34xrN5uBLnEoTKQUgDLgZ6hliLunBaIDhy4LYhyotptZlphGyLUhfyspxxj3AIpaVqikdgyzoGn7p0xNj71rNamweCscWC0qoQ8YRm3K2OgpeFoc+j9FSUYKB+4OgxIK4RcZUJ6RsUgqCrShxWzza9035aw/lzYGY5P4xFSMR5vMcFpm87opL4HjXsr76dLhC2xYhgx3I0BfoS7RCp+3K/e8vn+Ke2zWK+cYofQG9yMlw1eK1aAni9oSWil9eOmFhXkPnbXZ1eXqwVsirfQU9Vynm75lymLbxvpSP4yqI4iR5uWlFxdOI56Xbro5t3qhOrW7ZmL1EOFwp7k6pRXuWaZgBmuwJSIl1fNXXvrxjRTLy2ZTm1v9YeTBXedNbCYZZ1U4pdt+NGiomuKKEvKp5ZM/f5z9zctc1vju1b9cv5q/M/icBd4+KNztlnGWKfYjAMqm+K7zZ/PYP6d+X3TrafbmR8N71QcrOPMLd5RGdj838WFup393orNLWRki6vFv197661i40m6AKwYLneG79BzDPNhNYFWwnfguGyKgPl32bwseoTnKekVpS9n49vorWwv1JsSVwAJHCHcW2Agsk3rBBZXBihhcn11biTfDixpPik1bEZyj34EVXXzJrUccWwrbZo5+B6ztRpvO1kLjjO5qW3YccZ5JeTAecQxqqV0Q6hM5KVIrNL5a/77yQPUyLbK9qiMv49zFhW6MMnPE0dwxlQ48ckXDNHJOq0C2xByreHtxhPk1sK4DEI5dut7+QWCZCyj9MXKLWmD/gl1Xtfhd6F2CI86dv+XiIrdOpeeCDd0VyW7KGbLptn9p/mrgNsIxwzKN0QO3IvlPgAEA3AQhIZtaN54AAAAASUVORK5CYII=",
                            "contentType": "image/png",
                            "width": 15.75,
                            "height": 21.75
                        }
                    }
                ],
                "geometryType": "esriGeometryPoint"
            },
            "nextObjectId": 1
        }

        input_layer_url = ""
        if isinstance(input_layer, Item):
            if input_layer.type.lower() == 'feature service':
                input_param = {"url": input_layer.layers[0].url}
            elif input_layer.type.lower() == 'feature collection':
                fcdict = input_layer.get_data()
                fc = FeatureCollection(fcdict['layers'][0])
                input_param = fc.layer
            else:
                raise TypeError("item type must be feature service or feature collection")

        elif isinstance(input_layer, FeatureLayerCollection):
            input_layer_url = input_layer.layers[0].url  # ["url"]
            input_param = {"url": input_layer_url}
        elif isinstance(input_layer, FeatureCollection):
            input_param = input_layer.properties
        elif isinstance(input_layer, Layer):
            input_layer_url = input_layer.url
            input_param = {"url": input_layer_url}
        elif isinstance(input_layer, tuple):  # geocoding location, convert to point featureset
            input_param = point_fs
            input_param["featureSet"]["features"][0]["geometry"]["x"] = input_layer[1]
            input_param["featureSet"]["features"][0]["geometry"]["y"] = input_layer[0]
        elif isinstance(input_layer, dict):  # could add support for geometry one day using geometry -> featureset
            input_param = input_layer
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
            input_param = {"url": input_layer_url}
        else:
            raise Exception(
                "Invalid format of input layer. url string, feature service Item, feature service instance or dict supported")

        return input_param

    def _raster_input(self, input_raster):
        if isinstance(input_raster, Item):
            if input_raster.type.lower() == 'image service':
                input_param = {"itemId": input_raster.itemid}
            else:
                raise TypeError("item type must be image service")
        elif isinstance(input_raster, str):
            input_param = {"url": input_raster}
        elif isinstance(input_raster, dict):
            input_param = input_raster
        else:
            raise Exception("Invalid format of input raster. image service Item or image service url, cloud raster uri "
                            "or shared data path supported")

        return input_param


class Toolbox(_AsyncResource):
    "A collection of geoprocessing tools."

    def __init__(self, url, gis):
        """
        Constructs a Geoprocessing toolbox
        """
        super(Toolbox, self).__init__(url, gis)


        self._taskurls = {}
        self._param_names = {} # mapping from fn to name-map (camel_case (PEP8ified) parameter name to GP_Param_Name)
        self._method_params = {}

        for task in self.properties.tasks:
            fnname = _camelCase_to_underscore(task)
            # print("Function: " + fnname)

            taskurl = self.url + "/" + task

            self._taskurls[fnname] = taskurl + "/execute"

            taskprops = self._con.post(taskurl, {"f":"json"}, token=self._token)
            execution_type = taskprops['executionType']
            task_params = taskprops['parameters']

            helpstring = '\n'
            if 'docstring' in taskprops:
                helpstring = helpstring + ". " + taskprops['docstring']

            helpstring = helpstring + "\n\n\nParameters:\n"


            spec = []
            name_type = {}
            name_name = {} # map from camel_case to GPParameterName
            name_type[fnname] = task
            return_values = []
            for param in task_params:

                gp_param_name = param['name']

                param_name = _camelCase_to_underscore(gp_param_name)

                name_name[param_name] = gp_param_name

                param_type = param['dataType']
                param_dval = param['defaultValue']
                param_drtn = param['direction']

                param_rqrd = param['parameterType']

                param_choices = param.get('choiceList', None)

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
                elif param_type == 'GPFeatureRecordSetLayer':
                    py_param_type_ = FeatureSet
                elif param_type == 'GPRecordSet':
                    py_param_type_ = FeatureSet
                elif param_type == 'GPLinearUnit':
                    py_param_type_ = LinearUnit
                elif param_type == 'GPDataFile':
                    py_param_type_ = DataFile
                elif param_type == 'GPRasterData':
                    py_param_type_ = RasterData
                elif param_type == 'GPRasterLayer':
                    py_param_type_ = RasterData
                elif param_type.startswith('GPMultiValue'):
                    py_param_type_ = list
                else:
                    py_param_type_ = str

                if param_drtn == 'esriGPParameterDirectionInput':
                    name_type[param_name] = py_param_type_
                    # print("\n   " + param_name + " : " + str(py_param_type_))
                    #if param_dval is not None and param_dval != '':
                    #    print(" = " + str(param_dval))
                    #if param_rqrd is not None and param_rqrd == 'esriGPParameterTypeOptional':
                    #    print(" = None")
                    param_spec = ( param_name , param_dval )
                    spec.append(param_spec)

                    helpstring = helpstring + "\n\n   " + param_name + ": " + param['displayName']  + " (" + py_param_type_.__name__ + ")."
                    if param_rqrd == 'esriGPParameterTypeOptional':
                        helpstring = helpstring + " Optional parameter. "
                    elif param_rqrd == 'esriGPParameterTypeRequired' and param_dval is None:
                        helpstring = helpstring + " Required parameter. "

                    if 'description' in param:
                        helpstring = helpstring + ' ' + param['description']

                    if param_choices is not None and len(param_choices) > 0:
                        helpstring = helpstring + '\n      Choice list:' + str(param_choices)

                elif param_drtn == 'esriGPParameterDirectionOutput':
                    name_type[param_name] = py_param_type_
                    name_type['return'] = py_param_type_
                    name_type['return_name'] = param_name
                    name_type['return_display_name'] = param['displayName']

                    return_values.append({"name":param_name, "display_name": param['displayName'], "type":py_param_type_})

            if len(return_values) == 1:
                helpstring = helpstring + "\n\nReturns: " + name_type['return_display_name'] + " (" + name_type['return'].__name__ + ")"
            else:
                name_type['return'] = tuple # for method spec, type hinting
                helpstring = helpstring + "\n\nReturns a named tuple with the following fields:"
                for retval in return_values:
                    helpstring = helpstring + '\n   ' + retval['name'] + ' (' + retval['display_name'] + ' of type: ' + retval['type'].__name__ + ')'

            helpstring = helpstring + "\n"

            if 'helpUrl' in taskprops:
                helpstring = helpstring + "\nSee " + taskprops['helpUrl'] + " for additional help."

            generatedfn = _call_generator(task, spec)
            generatedfn.__annotations__ = name_type
            generatedfn.__doc__ = helpstring

            setattr(self, fnname, types.MethodType(generatedfn, self))

            self._method_params[fnname] = name_type
            self._param_names[fnname] = name_name

        # http://www.arcgis.com/home/item.html?id=383c2039b89d43baa0010c3bf243b144
        # http://sampleserver1.arcgisonline.com/ArcGIS/rest/Services/Specialty/ESRI_Currents_World/GPServer

    def __str__(self):
         return '<Toolbox url:' + self.url + '>'

    def _execute(self, params):
        caller_fnname = inspect.stack()[1][3]

        # print("Will call " + url +  " with these parameters:")

        name_type = self._method_params[caller_fnname]
        name_name = self._param_names[caller_fnname]

        task_name = name_type[caller_fnname]
        url = self.url + "/" + task_name + "/execute"

        #---------------------in---------------------#

        for key, value in params.items():
            # print(k + " = " + str(v))
            if key in name_type:
                py_type = name_type[key]

                if py_type in [FeatureSet, LinearUnit, DataFile, RasterData]:
                    if type(value) in [FeatureSet, LinearUnit, DataFile, RasterData]:
                        params[key] = value.to_dict()
                elif py_type == datetime.datetime:
                    params[key] = _date_handler(params[key])
        #--------------------------------------------#

        params.update({ "f" : "json" })

        gp_params = {}

        for param_name, param_value in params.items():
            gp_param_name = name_name.get(param_name, param_name)
            gp_params[gp_param_name] = param_value

        # copy environment variables if set
        if 'env:outSR' not in params and arcgis.env.out_spatial_reference is not None:
            gp_params['env:outSR'] = arcgis.env.out_spatial_reference

        if 'env:processSR' not in params and arcgis.env.process_spatial_reference is not None:
            gp_params['env:processSR'] = arcgis.env.process_spatial_reference

        if 'returnZ' not in params and arcgis.env.return_z is not False:
            gp_params['returnZ'] = True

        if 'returnM' not in params and arcgis.env.return_m is not False:
            gp_params['returnM'] = True

        resp = None

        if self.properties.executionType == 'esriExecutionTypeSynchronous':
            resp = self._con.post(url, gp_params, token=self._token)

            output_dict = {}

            for result in resp['results']:
                ret_param_name = result['paramName']
                ret_type = name_type[ret_param_name]

                ret_val = None
                if ret_type in [FeatureSet, LinearUnit, DataFile, RasterData]:
                    jsondict = result['value']
                    result_obj = ret_type.from_dict(jsondict)
                    result_obj._con = self._con
                    result_obj._token = self._token
                    ret_val = result_obj
                else:
                    ret_val = result['value']

                output_dict[ret_param_name] = ret_val


            num_returns = len(resp['results'])
            if num_returns == 1:
                return output_dict[name_type['return_name']]
            else:
                return output_dict

        else:
            task_url = "{}/{}".format(self.url, task_name)
            submit_url = "{}/submitJob".format(task_url)

            # arams["f"] = "json"

            job_info = self._con.post(submit_url, gp_params, token=self._token)

            job_info = super()._analysis_job_status(task_url, job_info)
            resp = super()._analysis_job_results(task_url, job_info)
            # print('***'+str(resp))

            output_dict = {}
            for retParamName in resp.keys():
                ret_param_name = _camelCase_to_underscore(retParamName)
                ret_type = name_type[ret_param_name]
                ret_val = None
                if ret_type in [FeatureSet, LinearUnit, DataFile, RasterData]:
                    jsondict = resp[retParamName]
                    result = ret_type.from_dict(jsondict)
                    result._con = self._con
                    result._token = self._token
                    ret_val =  result
                else:
                    ret_val = resp[retParamName]

                output_dict[ret_param_name] = ret_val

            num_returns = len(resp)
            if num_returns == 1:
                return output_dict[name_type['return_name']]
            else:
                return collections.namedtuple('GeoprocessingResults', output_dict.keys())(**output_dict)


    # def execute(self, task, input,
    #             outSR=None,
    #             processSR=None,
    #             returnZ=False,
    #             returnM=False):
    #
    #     # http://sampleserver1.arcgisonline.com/ArcGIS/rest/services/Specialty/ESRI_Currents_World/GPServer/MessageInABottle/execute? Input_Point={"features":[{"geometry":{"x":0,"y":0}}]}& Days=50
    #     url = self.url + "/" + task + "/execute"
    #     params = {
    #         "f" : "json",
    #     }
    #
    #     if outSR is not None:
    #         params['outSR'] = outSR
    #     if processSR is not None:
    #         params['processSR'] = processSR
    #     if returnZ:
    #         params['returnZ'] = "true"
    #     if returnM:
    #         params['returnM'] = "true"
    #
    #     for k, v in input.items():
    #         params[k] = v
    #
    #     resp = self.item._portal.con.post(url, params)
    #     return resp


