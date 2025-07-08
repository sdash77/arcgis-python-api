from __future__ import annotations
import logging
from typing import Any, Optional

import requests
from arcgis.gis import GIS, Item
from arcgis.raster._realitymapping import RMProject
from ._util import _update_settings, _validate_settings, get_request, post_request

_LOGGER = logging.getLogger(__name__)


class RMMission:
    """

    RMMission represents a mission in an Realitymapping Project.

    .. note :: This class is not created by users directly. An instance of this class is returned as output for
      get_mission() and add_mission() methods on the RMProject class of arcgis.raster.realitymapping module.

    ====================================     ====================================================================
    **Parameter**                             **Description**
    ------------------------------------     --------------------------------------------------------------------
    mission_name                             Required string representing the mission name.

                                             Example:

                                                mission_name='Mission_Yucaipa'
    ------------------------------------     --------------------------------------------------------------------
    project                                  Required RMProject object or an Realitymapping Project portal item. The realitymapping project to which the mission belongs to.
    ====================================     ====================================================================

    .. code-block:: python

        # Example Usage 1

        rm_item = gis.content.get("85a54236c6364a88a7c7c2b1a31fd901")
        project = RMProject(rm_item, gis=gis)

        mission_1 = project.add_mission(image_list,
                                        mission_name="mission_name",
                                        image_collection="img_collection",
                                        raster_type_name="UAV/UAS",
                                        raster_type_params=raster_type_params)

        # Example Usage 2

        rm_item = gis.content.get("85a54236c6364a88a7c7c2b1a31fd901")
        project = RMProject(rm_item, gis=gis)

        mission_1 = project.get_mission("mission_name")

    """

    def __init__(self, mission_name, mission_id, project):
        self._mission_name = mission_name
        self._mission_id = mission_id
        if isinstance(project, RMProject):
            self._project = project
        elif isinstance(project, Item):
            if project.type == "Reality Mapping Project":  # "Reality Mapping Project"
                self._project = RMProject(project, gis=project._gis)

        self._project_item = project._project_item
        self._gis = project._gis
        self._collection = None
        self._prod_to_id_map = {}
        self._reality_url = self._gis._url[:self._gis._url.find(".com")+4] + ":6443/arcgis/reality/api"
        self._workspace = self._mission_json.get("workspace", None)

    @property
    def _mission_json(self):
        return self._get_mission_json()
    
    @property
    def mission_id(self):
        return self._mission_id

    @property
    def products(self):
        """
        The ``products`` property returns all the products associated with the mission

        :return: A list of products of the mission
        """
        mission_products = {}
        self._prod_to_id_map = {}
        dataprod_mapping = {
            "orthoDEM": "dem",
            "qualityReport": "report",
            "mesh": "mesh",
            "DTM": "dtm",
            "mosaicDataset": "image_collection",
            "DSM": "dsm",
            "trueOrtho": "true_ortho",
            "DSMMesh": "dsm_mesh",
            "orthoMosaic": "ortho",
            "pointCloud": "point_cloud",
        }

        url = f"{self._reality_url}/missions/{self._mission_id}/dataproducts"
        headers = {"Authorization": f"Bearer {self._gis.session.auth.token}"}
        products = get_request(url, headers=headers)
        if products is None:
            _LOGGER.warning("No products found for this mission.")
            return mission_products
        for product in products:
            prod_type = product["interpretation"]
            prod_type = dataprod_mapping[prod_type] if prod_type in dataprod_mapping else prod_type
            mission_products[prod_type] = product["arcgisItem"]
            self._prod_to_id_map[prod_type] = product["id"]

        return mission_products

    @property
    def image_count(self):
        """
        The ``image_count`` property returns the number of images in the mission

        :return: An integer representing the number of images
        """
        ic = self.image_collection
        lyr = ic.layers[0]
        image_count = lyr.query(return_count_only=True)
        return image_count

    @property
    def mission_date(self):
        """
        The ``mission_date`` property returns the creation date & time of the mission.

        :return: A datetime object representing the mission date & time
        """
        from datetime import datetime
        ts = self._mission_json["created"]
        dt_obj = datetime.fromisoformat(ts.rstrip("Z"))
        return dt_obj

    @property
    def image_collection(self):
        """
        The ``image_collection`` property returns the image collection associated with the mission

        :return: image collection item
        """
        if self._collection is not None:
            return self._collection
        else:
            products = self.products
            img_coll = products.get("image_collection", None)
            if img_coll is not None:
                if "itemId" in img_coll:
                    self._collection = self._gis.content.get(img_coll["itemId"])
            else:
                _LOGGER.warning("No image collection found for this mission.")
        return self._collection

    @property
    def workspace(self):
        """
        The ``workspace`` property returns the workspace created for the reality mapping mission on the server

        :return: A string representing the workspace name
        """
        if self._workspace is not None:
            return self._workspace
        
        import json
        metadata = {}
        try:
            if "metadata" in self._mission_json:
                metadata = json.loads(self._mission_json["metadata"])
                self._workspace = metadata.get("workspace", None)
        except:
            pass
        return self._workspace
    
    @property
    def settings(self):
        return self._mission_json.get("processingSettings", {})

    @settings.setter
    def settings(self, new_settings):
        """
        The ``settings`` method updates the properties of the mission.
        """
        if new_settings is None:
            raise ValueError("new_settings cannot be None")
        
        current_settings = self.settings
        is_valid = _validate_settings(current_settings, new_settings)
        
        if not is_valid:
            raise ValueError("Invalid settings provided.")
        
        # update the current settings with the new settings
        _update_settings(current_settings, new_settings)
        payload = {"processingSettings": current_settings}
        
        url = f"{self._reality_url}/missions/{self.mission_id}/update"
        headers = {"Authorization": f"Bearer {self._gis.session.auth.token}"}
        resp = post_request(url, payload=payload, headers=headers)
        if resp is None:
            raise RuntimeError("Failed to update mission settings.")

    def _get_mission_json(self):
        url = f"{self._reality_url}/missions/{self._mission_id}"
        headers = {"Authorization": f"Bearer {self._gis.session.auth.token}"}
        resp = get_request(url=url, headers=headers)
        if resp is None:
            raise RuntimeError(f"Failed to retrieve settings.")
        return resp

    def delete(self):
        """
        The ``delete`` method deletes the RMMission and all the associated products.

        :return: A boolean indicating whether the deletion was successful or not
        """
        return self._gis._tools.realitymapping.delete_mission(self, future=False)


    def add_image(
        self,
        input_rasters: list,
        raster_type_name: Optional[str] = None,
        raster_type_params: Optional[dict[str, Any]] = None,
        context: Optional[dict[str, Any]] = None,
    ):
        """
        Add a collection of images to existing image collection of the mission. It provides provision to specify image collection properties through context parameter.

        It can be used when new data is available to be included in the same mission of the
        realitymapping project. When new data is added to the image collection
        the entire image collection must be reset to the original state.

        ==================                   ====================================================================
        **Parameter**                         **Description**
        ------------------                   --------------------------------------------------------------------
        input_rasters                        Required, the list of input images to be added to
                                             the image collection being created. This parameter can
                                             be a list of image paths or a path to a folder containing the images

                                             The function can create hosted imagery layers on enterprise from 
                                             local raster datasets by uploading the data to the server.  
        ------------------                   --------------------------------------------------------------------
        raster_type_name                     Optional string. The name of the raster type to use for adding data to
                                             the image collection.


                                             Choice list:

                                                 | [
                                                 | "Aerial", "ASTER", "DMCII", "DubaiSat-2", "GeoEye-1", "GF-1 PMS", "GF-1 WFV",
                                                 | "GF-2 PMS", "GRIB", "HDF", "IKONOS", "Jilin-1", "KOMPSAT-2", "KOMPSAT-3",
                                                 | "Landsat 1-5 MSS", "Landsat 4-5 TM", "Landsat 7 ETM+", "Landsat 8", "Landsat 9",
                                                 | "NetCDF", "PlanetScope", "Pleiades-1", "Pleiades NEO", "QuickBird", "RapidEye",
                                                 | "Raster Dataset", "ScannedAerial", "Sentinel-2", "SkySat", "SPOT 5", "SPOT 6",
                                                 | "SPOT 7", "Superview-1", "Tiled Imagery Layer", "UAV/UAS", "WordView-1",
                                                 | "WordView-2", "WordView-3", "WordView-4", "ZY3-SASMAC", "ZY3-CRESDA"
                                                 | ]
                                         

                                             Example:

                                                "QuickBird"
        ------------------                   --------------------------------------------------------------------
        raster_type_params                   Optional dict. Additional ``raster_type`` specific parameters.
        
                                             The process of add rasters to the image collection can be \
                                             controlled by specifying additional raster type arguments.

                                             The raster type parameters argument is a dictionary.
                                         
                                             Syntax:

                                                 {"gps": [["image1.jpg", "10", "2", "300"], ["image2.jpg", "10", "3", "300"], ["image3.jpg", "10", "4", "300"]],
                                                 "cameraProperties": {"Maker": "Canon", "Model": "5D Mark II", "FocalLength": 20, "PixelSize": 10, "x0": 0, "y0": 0, "columns": 4000, "rows": 3000},
                                                 "constantZ": 300,"isAltitudeFlightHeight": "True","dem": {"url": ``https://...``}

                                             The dictionary can contain productType, processingTemplate, \
                                             pansharpenType, Filter, pansharpenWeights, ConstantZ, \
                                             dem, zoffset, CorrectGeoid, ZFactor, StretchType, \
                                             ScaleFactor, ValidRange

                                             Please check the table below (Supported Raster Types), \
                                             for more details about the product types, \
                                             processing templates, pansharpen weights for each raster type. 

                                             - Possible values for pansharpenType - ["Mean", "IHS", "Brovey", "Esri", "Mean", "Gram-Schmidt"]
                                             - Possible values for filter - [None, "Sharpen", "SharpenMore"]
                                             - Value for StretchType dictionary can be as follows:

                                               - "None"
                                               - "MinMax; <min>; <max>"
                                               - "PercentMinMax; <MinPercent>; <MaxPercent>"
                                               - "StdDev; <NumberOfStandardDeviation>"
                                               Example: {"StretchType": "MinMax; <min>; <max>"}
                                             - Value for ValidRange dictionary can be as follows:

                                               - "<MaskMinValue>, <MaskMaxValue>"
                                               Example: {"ValidRange": "10, 200"}

                                             Example:

                                                {"productType":"All","processingTemplate":"Pansharpen",
                                                "pansharpenType":"Gram-Schmidt","filter":"SharpenMore",
                                                "pansharpenWeights":"0.85 0.7 0.35 1","constantZ":-9999}
        ------------------                   --------------------------------------------------------------------
        context                              Optional dict. The context parameter is used to provide additional input parameters.

                                             Syntax:

                                                {"image_collection_properties": {"imageCollectionType":"Satellite"},"byref":'True'}
                                            
                                             Use ``image_collection_properties`` key to set value for imageCollectionType.


                                             .. note::

                                                The "imageCollectionType" property is important for image collection that will later on be adjusted by realitymapping system service.
                                                Based on the image collection type, the realitymapping system service will choose different algorithm for adjustment.
                                                Therefore, if the image collection is created by reference, the requester should set this
                                                property based on the type of images in the image collection using the following keywords.
                                                If the imageCollectionType is not set, it defaults to "UAV/UAS"
 
                                             If byref is set to 'True', the data will not be uploaded. If it is not set, the default is 'False'
        ==================                   ====================================================================

        :return: The imagery layer url


        """
        image_collection = self.image_collection

        from arcgis.raster.analytics import add_image

        gis = self._gis

        if context is None:
            context = {"mission": self.mission_id, "workspace": self.workspace}
        else:
            context["mission"] = self.mission_id
            context["workspace"] = self.workspace

        gpjob = add_image(
            image_collection=image_collection,
            input_rasters=input_rasters,
            raster_type_name=raster_type_name,
            raster_type_params=raster_type_params,
            context=context,
            gis=gis,
            future=True,
        )

        return image_collection.url

    def delete_image(self, where: str):
        """

        ``delete_image`` allows users to remove existing images from the image collection (mosaic dataset) of a mission.

        ==================                   ====================================================================
        **Parameter**                         **Description**
        ------------------                   --------------------------------------------------------------------
        where                                Required string. A SQL ``where`` clause for selecting the images
                                             to be deleted from the image collection
        ==================                   ====================================================================

        :return: The imagery layer url

        """

        image_collection = self.image_collection

        from arcgis.raster.analytics import delete_image

        gis = self._gis

        if context is None:
            context = {"mission": self.mission_id}
        else:
            context["mission"] = self.mission_id

        gpjob = delete_image(
            image_collection=image_collection, where=where, gis=gis, future=True
        )

        return image_collection.url

    def __repr__(self):
        return "<%s - %s>" % (type(self).__name__, self._mission_name)
