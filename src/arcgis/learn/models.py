"Functions for model package management" 

from arcgis.geoprocessing._support import _analysis_job, _analysis_job_results, \
                                          _analysis_job_status, _layer_input
import json as _json
import arcgis as _arcgis
from arcgis.gis import Item


class Model:
    def __init__(self, model = None):
        if isinstance(model, Item):
            self._model = _json.dumps({ "itemId" : model.itemid })
            self._model_package = True


    def from_json(self, model):
        """
        Function is used to initialise Model object from model definition JSON
        eg usage:
        model = Model()
        model.from_json({"Framework" :"TensorFlow", 
                        "ModelConfiguration":"DeepLab", 
                        "InferenceFunction":"[functions]System\\DeepLearning\\ImageClassifier.py", 
                        "ModelFile":"\\\\uaenas1\\CRData\\ArcGIS_Pro_2_3\\ImageClassification\\tensorflow\\model\\frozen_inference_graph.pb", 
                        "ExtractBands":[0,1,2], 
                        "ImageWidth":513, 
                        "ImageHeight":513, 
                        "Classes": [ { "Value":0, "Name":"Evergreen Forest", "Color":[0, 51, 0] }, 
                                    { "Value":1, "Name":"Grassland/Herbaceous", "Color":[241, 185, 137] }, 
                                    { "Value":2, "Name":"Bare Land", "Color":[236, 236, 0] }, 
                                    { "Value":3, "Name":"Open Water", "Color":[0, 0, 117] }, 
                                    { "Value":4, "Name":"Scrub/Shrub", "Color":[102, 102, 0] }, 
                                    { "Value":5, "Name":"Impervious Surface", "Color":[236, 236, 236] } ] })

        """
        if isinstance(model, dict):
            self._model = model
            self._model_package = False
            
    def from_model_path(self, model):
        """
        Function is used to initialise Model object from url of model package or path of model definition file
        eg usage:
        model = Model()
        model.from_model_path("https://xxxportal.esri.com/sharing/rest/content/items/bf5bad4cdbe144ba8edd6dd11e01e7e1")

        or
        model = Model()
        model.from_model_path("\\\\sharedstorage\\sharefolder\\findtrees.emd")

        """
        if 'http:' in model or 'https:' in model:
            self._model = _json.dumps({ 'url' : model })
            self._model_package = True
        else:
            self._model = _json.dumps({ 'uri' : model })
            self._model_package = False
            

    def install(self, gis=None):

        """
        Function is used to install the uploaded model package (*.dlpk). Optionally after inferencing 
        the necessary information using the model, the model can be uninstalled by uninstall_model() 


        ==================     ====================================================================
        **Argument**           **Description**                     
        ------------------     --------------------------------------------------------------------
        gis                    Optional GIS. The GIS on which this tool runs. If not specified, the active GIS is used.
        ==================     ====================================================================

        :return:
            Path where model in installed

        """
        if self._model_package is False:
            raise RuntimeError("model object should be created from a portal item or a portal url")

        task = "InstallDeepLearningModel"

        gis = _arcgis.env.active_gis if gis is None else gis
        url = gis.properties.helperServices.rasterAnalytics.url
        gptool = _arcgis.gis._GISResource(url, gis)

        params = {}

        if self._model is None:
            raise RuntimeError("For install/uninstall model object should be created from a portal item or portal url")
        else:   
            params["modelPackage"] = self._model

        task_url, job_info, job_id = _analysis_job(gptool, task, params)

        job_info = _analysis_job_status(gptool, task_url, job_info)
        job_values = _analysis_job_results(gptool, task_url, job_info, job_id)
        item_properties = {
            "properties": {
                "jobUrl": task_url + '/jobs/' + job_info['jobId'],
                "jobType": "GPServer",
                "jobId": job_info['jobId'],
                "jobStatus": "completed"
            }
        }

        return job_values["installSucceed"]


    def query_info(self, gis=None):

        """
        Function is used to extract the deep learning model specific settings from the model package item or model definition file.

        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        gis                    Optional GIS. The GIS on which this tool runs. If not specified, the active GIS is used.
        ==================     ====================================================================

        :return:
           The key model information in dictionary format that describes what the settings are essential for this type of deep learning model.
        """


        task = "QueryDeepLearningModelInfo"

        gis = _arcgis.env.active_gis if gis is None else gis
        url = gis.properties.helperServices.rasterAnalytics.url
        gptool = _arcgis.gis._GISResource(url, gis)

        params = {}

        if self._model is None:
            raise RuntimeError('model cannot be None')
        else:
            params["model"] = self._model

        task_url, job_info, job_id = _analysis_job(gptool, task, params)

        job_info = _analysis_job_status(gptool, task_url, job_info)
        job_values = _analysis_job_results(gptool, task_url, job_info, job_id)
        item_properties = {
            "properties": {
                "jobUrl": task_url + '/jobs/' + job_info['jobId'],
                "jobType": "GPServer",
                "jobId": job_info['jobId'],
                "jobStatus": "completed"
            }
        }
        output = job_values["outModelInfo"]
        try:
           dict_output =  _json.loads(output["modelInfo"])
           return dict_output
        except:
            return output


    def uninstall(self, gis=None):

        """
        Function is used to uninstall the uploaded model package that was installed using the install_model() 
        This function will delete the named deep learning model from the server but not the portal item.

        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        gis                    Optional GIS. The GIS on which this tool runs. If not specified, the active GIS is used.
        ==================     ====================================================================

        :return:
            itemId of the uninstalled model package item

        """
        if self._model_package is False:
            raise RuntimeError("For install/uninstall model object should be created from a portal item or a portal url")

        task = "UninstallDeepLearningModel"

        gis = _arcgis.env.active_gis if gis is None else gis
        url = gis.properties.helperServices.rasterAnalytics.url
        gptool = _arcgis.gis._GISResource(url, gis)

        params = {}

        if self._model is None:
            raise RuntimeError('model_package cannot be None')
        else:   
            params["modelItemId"] = self._model

        task_url, job_info, job_id = _analysis_job(gptool, task, params)

        job_info = _analysis_job_status(gptool, task_url, job_info)
        job_values = _analysis_job_results(gptool, task_url, job_info, job_id)
        item_properties = {
            "properties": {
                "jobUrl": task_url + '/jobs/' + job_info['jobId'],
                "jobType": "GPServer",
                "jobId": job_info['jobId'],
                "jobStatus": "completed"
            }
        }

        return job_values["uninstallSucceed"]



def list_models(gis=None):
    """
    Function is used to list all the installed deep learning models.

    ==================     ====================================================================
    **Argument**           **Description**
    ------------------     --------------------------------------------------------------------
    gis                    Optional GIS. The GIS on which this tool runs. If not specified, the active GIS is used.
    ==================     ====================================================================

    :return:
        list of deep learning models installed

    """



    task = "ListDeepLearningModels"

    gis = _arcgis.env.active_gis if gis is None else gis
    url = gis.properties.helperServices.rasterAnalytics.url
    gptool = _arcgis.gis._GISResource(url, gis)

    params = {}
    task_url, job_info, job_id = _analysis_job(gptool, task, params)

    job_info = _analysis_job_status(gptool, task_url, job_info)
    job_values = _analysis_job_results(gptool, task_url, job_info, job_id)
    item_properties = {
        "properties": {
            "jobUrl": task_url + '/jobs/' + job_info['jobId'],
            "jobType": "GPServer",
            "jobId": job_info['jobId'],
            "jobStatus": "completed"
        }
    }

    return job_values["deepLearningModels"]



