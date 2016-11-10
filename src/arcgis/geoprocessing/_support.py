import datetime

import inspect
import logging
import sys
import time
import datetime
import collections

import arcgis
from arcgis.gis import GIS
from arcgis.features import FeatureSet
from arcgis.mapping import MapImageLayer
from arcgis.geoprocessing import DataFile, LinearUnit, RasterData
from arcgis.geoprocessing.tool import _camelCase_to_underscore
from arcgis._impl.common._utils import _date_handler

_log = logging.getLogger(__name__)

def _analysis_job_status(gptool, task_url, job_info):
    """ Tracks the status of the submitted Analysis job."""

    if "jobId" in job_info:
        # Get the id of the Analysis job to track the status.
        #
        job_id = job_info.get("jobId")
        job_url = "{}/jobs/{}".format(task_url, job_id)
        params = {"f": "json"}
        job_response = gptool._con.post(job_url, params, token=gptool._token)

        # Query and report the Analysis job status.
        #
        num_messages = 0

        if "jobStatus" in job_response:
            while not job_response.get("jobStatus") == "esriJobSucceeded":
                time.sleep(1)

                job_response = gptool._con.post(job_url, params, token=gptool._token)
                # print(job_response)
                messages = job_response['messages'] if 'messages' in job_response else []
                num = len(messages)
                if num > num_messages:
                    for index in range(num_messages, num):
                        msg = messages[index]
                        if msg['type'] == 'esriJobMessageTypeInformative':
                            _log.info(msg['description'])
                        elif msg['type'] == 'esriJobMessageTypeWarning':
                            _log.warn(msg['description'])
                        elif msg['type'] == 'esriJobMessageTypeError':
                            _log.error(msg['description'])
                            print(msg['description'], file=sys.stderr)
                        else:
                            _log.warn(msg['description'])  # ,file = sys.stderr)
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


def _analysis_job_results(gptool, task_url, job_info):
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
                    param_result = gptool._con.post(result_url, params, token=gptool._token)

                    job_value = param_result.get("value")
                    result_values[key] = job_value
            return result_values
        else:
            raise Exception("Unable to get analysis job results.")
    else:
        raise Exception("Unable to get analysis job results.")


def _execute_gp_tool(gis, task_name, params, param_db, return_values, use_async, url):
    if gis is None:
        gis = arcgis.env.active_gis

    gp_params = {"f": "json"}

    # ---------------------in---------------------#
    for param_name, param_value in params.items():
        #print(param_name + " = " + str(param_value))
        if param_name in param_db:
            py_type, gp_param_name = param_db[param_name]
            gp_params[gp_param_name] = param_value
            if py_type in [FeatureSet, LinearUnit, DataFile, RasterData]:
                if type(param_value) in [FeatureSet, LinearUnit, DataFile, RasterData]:
                    gp_params[gp_param_name] = param_value.to_dict()

                elif type(param_value) == str:

                    try:
                        klass = py_type
                        gp_params[gp_param_name] = klass.from_str(param_value)

                    except sys.Error as e:
                        pass
            elif py_type == datetime.datetime:
                gp_params[gp_param_name] = _date_handler(param_value)
    # --------------------------------------------#

    _set_env_params(gp_params, params)

    # for param_name, param_value in gp_params.items():
    #     print(param_name + " = " + str(param_value))

    gptool = arcgis.gis._GISResource(url, gis)

    if use_async:
        task_url = "{}/{}".format(url, task_name)
        submit_url = "{}/submitJob".format(task_url)

        job_info = gptool._con.post(submit_url, gp_params, token=gptool._token)
        job_info = _analysis_job_status(gptool, task_url, job_info)
        resp = _analysis_job_results(gptool, task_url, job_info)

        # ---------------------async-out---------------------#
        output_dict = {}
        for retParamName in resp.keys():
            output_val = resp[retParamName]
            ret_param_name, ret_val = _get_output_value(gptool, output_val, param_db, retParamName)
            output_dict[ret_param_name] = ret_val

        # tools with output map service - add another output:
        # result_layer = '' #***self.properties.resultMapServerName
        if gptool.properties.resultMapServerName != '':
            job_id = job_info.get("jobId")
            result_layer_url = url.replace('/GPServer', '/MapServer') + '/jobs/' + job_id

            output_dict['result_layer'] = MapImageLayer(result_layer_url, gptool._gis)

        num_returns = len(resp)
        return _return_output(num_returns, output_dict, return_values)

    else: # synchronous
        exec_url = url + "/" + task_name + "/execute"
        resp = gptool._con.post(exec_url, gp_params, token=gptool._token)

        output_dict = {}

        for result in resp['results']:
            retParamName = result['paramName']

            output_val = result['value']
            ret_param_name, ret_val = _get_output_value(gptool, output_val, param_db, retParamName)
            output_dict[ret_param_name] = ret_val

        num_returns = len(resp['results'])
        return _return_output(num_returns, output_dict, return_values)


def _set_env_params(gp_params, params):
    # copy environment variables if set
    if 'env:outSR' not in params and arcgis.env.out_spatial_reference is not None:
        gp_params['env:outSR'] = arcgis.env.out_spatial_reference
    if 'env:processSR' not in params and arcgis.env.process_spatial_reference is not None:
        gp_params['env:processSR'] = arcgis.env.process_spatial_reference
    if 'returnZ' not in params and arcgis.env.return_z is not False:
        gp_params['returnZ'] = True
    if 'returnM' not in params and arcgis.env.return_m is not False:
        gp_params['returnM'] = True


def _return_output(num_returns, output_dict, return_values):
    if num_returns == 1:
        return output_dict[return_values[0]['name']]
    else:
        ret_names = []
        for return_value in return_values:
            ret_names.append(return_value['name'])

        NamedTuple = collections.namedtuple('ToolOutput', ret_names)
        tool_output = NamedTuple(**output_dict)
        return tool_output


def _get_output_value(gptool, output_val, param_db, retParamName):
    ret_param_name = _camelCase_to_underscore(retParamName)
    ret_type, _ = param_db[ret_param_name]
    ret_val = None
    if ret_type in [FeatureSet, LinearUnit, DataFile, RasterData]:
        jsondict = output_val
        if 'mapImage' in jsondict:  # http://resources.esri.com/help/9.3/arcgisserver/apis/rest/gpresult.html#mapimage
            ret_val = jsondict
        else:
            result = ret_type.from_dict(jsondict)
            result._con = gptool._con
            result._token = gptool._token
            ret_val = result
    else:
        ret_val = output_val
    return ret_param_name, ret_val
