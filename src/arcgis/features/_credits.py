"""

Contains an internal GP method used to calculate Credit Usage for Tool
This is a private method and could change without warning. Do not use.

"""
import json
import arcgis as _arcgis
from arcgis.geoprocessing import DataFile, LinearUnit, RasterData
from arcgis.geoprocessing._support import _execute_gp_tool

def _estimate_credits(task, parameters, gis=None):
    """
    Estimates the number of credits a spatial analysis operation will take.



    :returns: float

    """

    if gis is None and \
       _arcgis.env.active_gis:
        gis = _arcgis.env.active_gis
    elif gis is None and \
         _arcgis.env.active_gis is None:
        raise Exception("A GIS must be provided and/or set as active.")
    isinstance(gis, _arcgis.GIS)
    if gis.version >= [7,1] and \
       gis._portal.is_arcgisonline:
        #https://analysisdev.arcgis.com/arcgis/rest/services/Estimate/GPServer/EstimateCredits/execute
        url = gis.properties['helperServices']['creditEstimation']['url']
        #from arcgis.geoprocessing import import_toolbox
        #tbx = import_toolbox(url)
        gptask = "EstimateCredits"
        url = "{base}/{gptask}/execute".format(base=url, gptask=gptask)
        params = {
            'f' : 'json',
            'taskName' : task,
            'taskParameters' : json.dumps(parameters)
        }

        kwargs = locals()

        param_db = {
            "task": (str, "taskName"),
            "parameters": (str, "taskParameters"),
            "credit_estimate": (str, "creditEstimate"),
        }
        return_values = [
            {"name":"credit_estimate", "display_name":"creditEstimate", "type":str},
        ]
        res = _execute_gp_tool(gis, gptask, kwargs, param_db, return_values, False, url, webtool=True, add_token=False)
        if 'cost' in res:
            return res['cost']
        return res
    return

if __name__ == "__main__":
    gis = _arcgis.GIS(profile='geodevagol', verify_cert=False)
    taskName = 'AggregatePoints'
    taskParameters = '''{"binType":"HEXAGON","binSize":2,"binSizeUnit":"Kilometers","pointLayer":"{\"url\":\"https://servicesdev.arcgis.com/01ClFLufh9nZafWR/arcgis/rest/services/TestData123a/FeatureServer/0\",\"serviceToken\":\"oCxG5fzz_pHu2SYUaV45H4PiSbgG87m49f_qb89Ydf5tqpyay7M8XTtpuuGQy9UnM9yHaEGr3RNpTSLR9ebTcgyg99dRpcfb0gXStqvKCgSc0irOOzd_ljv-hxyVMJKHJ8eeMnSxrSDFsBXSxjSD0RrSRhz4dFAfC7papu4fKKMPbmRwiaAXM1pKx7vooejbHs4wWxpYC8SbvpCkX4pD47UY0Ok7bOonhVARzSTY-71evajOJinwzz0QmP0BV1bQJ-3ZtQbws-KLpkHzmfrGR8tE0H_3FF8j7OnTfQCeE1fftalT1bm3y5zCMN7b5Ykj\",\"name\":\"TestData123a\"}","summaryFields":"[]","OutputName":"{\"serviceProperties\":{\"name\":\"Aggregation of TestData123a by hexagon bins\"}}","keepBoundariesWithNoPoints":"true","context":"{\"extent\":{\"xmin\":-10457994.159813268,\"ymin\":5623296.719129753,\"xmax\":-10402271.566193448,\"ymax\":5688956.126426631,\"spatialReference\":{\"wkid\":102100,\"latestWkid\":3857}}}"}'''

    result = _estimate_credits(task=taskName, parameters=taskParameters, gis=gis)
    print('result')