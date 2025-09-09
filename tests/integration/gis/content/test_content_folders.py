import os
import io
import uuid
import unittest
from arcgis.gis import Item, ItemProperties, ItemTypeEnum
from arcgis.gis._impl._content_manager import Folder, Folders
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging
from integration.config import get_resource_path, get_web_resource_path
from integration.config import INTEGRATION_TEST_ITEM_TAG
from utils.data_utils import cleanup_published_items
import pandas as pd
from arcgis.gis._impl._content_manager.folder import FolderException

enable_verbose_logging()

TEXT_DATA = {
    "operationalLayers": [
        {
            "id": "CA_Fire_Boundaries_9995",
            "layerType": "ArcGISMapServiceLayer",
            "url": "https://pythonapi.playground.esri.com/server/rest/services/CA_Fire_Boundaries/MapServer",
            "visibility": True,
            "opacity": 1,
            "title": "CA_Fire_Boundaries",
            "itemId": "3f736ece6c154aabaf8420247adbdecd",
        },
        {
            "id": "SanFranciscoDataLayers_4326_2624",
            "layerType": "ArcGISFeatureLayer",
            "url": "https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/12",
            "visibility": True,
            "opacity": 1,
            "mode": 1,
            "title": "SanFranciscoDataLayers_4326 - Parks",
            "itemId": "a144dd9463454fe99cbdedc86d6495ae",
            "popupInfo": {
                "title": "Parks: {name}",
                "fieldInfos": [
                    {
                        "fieldName": "objectid",
                        "label": "OBJECTID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "id",
                        "label": "ID",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                    {
                        "fieldName": "featarea",
                        "label": "FEATAREA",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                    {
                        "fieldName": "featperim",
                        "label": "FEATPERIM",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                    {
                        "fieldName": "name",
                        "label": "NAME",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "displtyp",
                        "label": "DISPLTYP",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 0, "digitSeparator": True},
                    },
                    {
                        "fieldName": "globalid",
                        "label": "GlobalID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "SHAPE__Length",
                        "label": "SHAPE__Length",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                    {
                        "fieldName": "SHAPE__Area",
                        "label": "SHAPE__Area",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                ],
                "description": None,
                "showAttachments": True,
                "mediaInfos": [],
            },
        },
        {
            "id": "SanFranciscoDataLayers_4326_5308",
            "layerType": "ArcGISFeatureLayer",
            "url": "https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/11",
            "visibility": True,
            "opacity": 1,
            "mode": 1,
            "title": "SanFranciscoDataLayers_4326 - Landmarks",
            "itemId": "a144dd9463454fe99cbdedc86d6495ae",
            "popupInfo": {
                "title": "Landmarks: {name}",
                "fieldInfos": [
                    {
                        "fieldName": "objectid",
                        "label": "OBJECTID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "name",
                        "label": "NAME",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "fcc",
                        "label": "FCC",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "globalid",
                        "label": "GlobalID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "SHAPE__Length",
                        "label": "SHAPE__Length",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                    {
                        "fieldName": "SHAPE__Area",
                        "label": "SHAPE__Area",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                ],
                "description": None,
                "showAttachments": True,
                "mediaInfos": [],
            },
        },
        {
            "id": "SanFranciscoDataLayers_4326_3522",
            "layerType": "ArcGISFeatureLayer",
            "url": "https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/10",
            "visibility": True,
            "opacity": 1,
            "mode": 1,
            "title": "SanFranciscoDataLayers_4326 - Highways",
            "itemId": "a144dd9463454fe99cbdedc86d6495ae",
            "popupInfo": {
                "title": "Highways: {name}",
                "fieldInfos": [
                    {
                        "fieldName": "objectid",
                        "label": "OBJECTID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "prefix",
                        "label": "PREFIX",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "pretype",
                        "label": "PRETYPE",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "name",
                        "label": "NAME",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "type",
                        "label": "TYPE",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "suffix",
                        "label": "SUFFIX",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "fcc",
                        "label": "FCC",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "acc",
                        "label": "ACC",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "shield",
                        "label": "SHIELD",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "hwy_num",
                        "label": "HWY_NUM",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "globalid",
                        "label": "GlobalID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "SHAPE__Length",
                        "label": "SHAPE__Length",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                ],
                "description": None,
                "showAttachments": True,
                "mediaInfos": [],
            },
        },
        {
            "id": "SanFranciscoDataLayers_4326_2877",
            "layerType": "ArcGISFeatureLayer",
            "url": "https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/9",
            "visibility": True,
            "opacity": 1,
            "mode": 1,
            "title": "SanFranciscoDataLayers_4326 - Rivers",
            "itemId": "a144dd9463454fe99cbdedc86d6495ae",
            "popupInfo": {
                "title": "Rivers: {name}",
                "fieldInfos": [
                    {
                        "fieldName": "objectid",
                        "label": "OBJECTID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "name",
                        "label": "NAME",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "fcc",
                        "label": "FCC",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "globalid",
                        "label": "GlobalID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "SHAPE__Length",
                        "label": "SHAPE__Length",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                ],
                "description": None,
                "showAttachments": True,
                "mediaInfos": [],
            },
        },
        {
            "id": "SanFranciscoDataLayers_4326_4178",
            "layerType": "ArcGISFeatureLayer",
            "url": "https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/8",
            "visibility": True,
            "opacity": 1,
            "mode": 1,
            "title": "SanFranciscoDataLayers_4326 - sf_stores",
            "itemId": "a144dd9463454fe99cbdedc86d6495ae",
            "popupInfo": {
                "title": "sf_stores: {store_id}",
                "fieldInfos": [
                    {
                        "fieldName": "objectid",
                        "label": "FID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "store_id",
                        "label": "STORE_ID",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "globalid",
                        "label": "GlobalID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                ],
                "description": None,
                "showAttachments": True,
                "mediaInfos": [],
            },
        },
        {
            "id": "SanFranciscoDataLayers_4326_9036",
            "layerType": "ArcGISFeatureLayer",
            "url": "https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/7",
            "visibility": True,
            "opacity": 1,
            "mode": 1,
            "title": "SanFranciscoDataLayers_4326 - sf_cust",
            "itemId": "a144dd9463454fe99cbdedc86d6495ae",
            "popupInfo": {
                "title": "sf_cust: {store_id}",
                "fieldInfos": [
                    {
                        "fieldName": "objectid",
                        "label": "FID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "store_id",
                        "label": "STORE_ID",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "globalid",
                        "label": "GlobalID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                ],
                "description": None,
                "showAttachments": True,
                "mediaInfos": [],
            },
        },
        {
            "id": "SanFranciscoDataLayers_4326_2413",
            "layerType": "ArcGISFeatureLayer",
            "url": "https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/6",
            "visibility": True,
            "opacity": 1,
            "mode": 1,
            "title": "SanFranciscoDataLayers_4326 - End Locations",
            "itemId": "a144dd9463454fe99cbdedc86d6495ae",
            "popupInfo": {
                "title": "End Locations: {status}",
                "fieldInfos": [
                    {
                        "fieldName": "objectid",
                        "label": "OBJECTID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "routeid",
                        "label": "RouteID",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 0, "digitSeparator": True},
                    },
                    {
                        "fieldName": "start_x",
                        "label": "Start_X",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                    {
                        "fieldName": "start_y",
                        "label": "Start_Y",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                    {
                        "fieldName": "end_x",
                        "label": "End_X",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                    {
                        "fieldName": "end_y",
                        "label": "End_Y",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                    {
                        "fieldName": "status",
                        "label": "Expected Status",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "globalid",
                        "label": "GlobalID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                ],
                "description": None,
                "showAttachments": True,
                "mediaInfos": [],
            },
        },
        {
            "id": "SanFranciscoDataLayers_4326_2775",
            "layerType": "ArcGISFeatureLayer",
            "url": "https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/5",
            "visibility": True,
            "opacity": 1,
            "mode": 1,
            "title": "SanFranciscoDataLayers_4326 - Start Locations",
            "itemId": "a144dd9463454fe99cbdedc86d6495ae",
            "popupInfo": {
                "title": "Start Locations: {status}",
                "fieldInfos": [
                    {
                        "fieldName": "objectid",
                        "label": "OBJECTID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "routeid",
                        "label": "RouteID",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 0, "digitSeparator": True},
                    },
                    {
                        "fieldName": "start_x",
                        "label": "Start_X",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                    {
                        "fieldName": "start_y",
                        "label": "Start_Y",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                    {
                        "fieldName": "end_x",
                        "label": "End_X",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                    {
                        "fieldName": "end_y",
                        "label": "End_Y",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                    {
                        "fieldName": "status",
                        "label": "Expected Status",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "globalid",
                        "label": "GlobalID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                ],
                "description": None,
                "showAttachments": True,
                "mediaInfos": [],
            },
        },
        {
            "id": "SanFranciscoDataLayers_4326_2872",
            "layerType": "ArcGISFeatureLayer",
            "url": "https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/4",
            "visibility": True,
            "opacity": 1,
            "mode": 1,
            "title": "SanFranciscoDataLayers_4326 - Stores",
            "itemId": "a144dd9463454fe99cbdedc86d6495ae",
            "popupInfo": {
                "title": "Stores: {name}",
                "fieldInfos": [
                    {
                        "fieldName": "objectid",
                        "label": "OBJECTID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "name",
                        "label": "NAME",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "demand",
                        "label": "Demand",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                    {
                        "fieldName": "servicetime",
                        "label": "ServiceTime",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                    {
                        "fieldName": "timestart1",
                        "label": "TimeStart1",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"dateFormat": "shortDateShortTime"},
                    },
                    {
                        "fieldName": "timeend1",
                        "label": "TimeEnd1",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"dateFormat": "shortDateShortTime"},
                    },
                    {
                        "fieldName": "globalid",
                        "label": "GlobalID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                ],
                "description": None,
                "showAttachments": True,
                "mediaInfos": [],
            },
        },
        {
            "id": "SanFranciscoDataLayers_4326_2726",
            "layerType": "ArcGISFeatureLayer",
            "url": "https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/3",
            "visibility": True,
            "opacity": 1,
            "mode": 1,
            "title": "SanFranciscoDataLayers_4326 - Distribution Center",
            "itemId": "a144dd9463454fe99cbdedc86d6495ae",
            "popupInfo": {
                "title": "Distribution Center: {name}",
                "fieldInfos": [
                    {
                        "fieldName": "objectid",
                        "label": "OBJECTID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "name",
                        "label": "NAME",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "globalid",
                        "label": "GlobalID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                ],
                "description": None,
                "showAttachments": True,
                "mediaInfos": [],
            },
        },
        {
            "id": "SanFranciscoDataLayers_4326_9300",
            "layerType": "ArcGISFeatureLayer",
            "url": "https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/2",
            "visibility": True,
            "opacity": 1,
            "mode": 1,
            "title": "SanFranciscoDataLayers_4326 - Fire Stations",
            "itemId": "a144dd9463454fe99cbdedc86d6495ae",
            "popupInfo": {
                "title": "Fire Stations: {name}",
                "fieldInfos": [
                    {
                        "fieldName": "objectid",
                        "label": "OBJECTID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "status",
                        "label": "Status",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "score",
                        "label": "Score",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 0, "digitSeparator": True},
                    },
                    {
                        "fieldName": "match_type",
                        "label": "Match_type",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "side",
                        "label": "Side",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "match_addr",
                        "label": "Match_addr",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "name",
                        "label": "NAME",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "address",
                        "label": "ADDRESS",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "globalid",
                        "label": "GlobalID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                ],
                "description": None,
                "showAttachments": True,
                "mediaInfos": [],
            },
        },
        {
            "id": "SanFranciscoDataLayers_4326_1710",
            "layerType": "ArcGISFeatureLayer",
            "url": "https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/1",
            "visibility": True,
            "opacity": 1,
            "mode": 1,
            "title": "SanFranciscoDataLayers_4326 - Hospitals",
            "itemId": "a144dd9463454fe99cbdedc86d6495ae",
            "popupInfo": {
                "title": "Hospitals: {name}",
                "fieldInfos": [
                    {
                        "fieldName": "objectid",
                        "label": "OBJECTID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "name",
                        "label": "NAME",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "fcc",
                        "label": "FCC",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "globalid",
                        "label": "GlobalID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                ],
                "description": None,
                "showAttachments": True,
                "mediaInfos": [],
            },
        },
        {
            "id": "SanFranciscoDataLayers_4326_7720",
            "layerType": "ArcGISFeatureLayer",
            "url": "https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/0",
            "visibility": True,
            "opacity": 1,
            "mode": 1,
            "title": "SanFranciscoDataLayers_4326 - Tract Centroids",
            "itemId": "a144dd9463454fe99cbdedc86d6495ae",
            "popupInfo": {
                "title": "Tract Centroids: {name}",
                "fieldInfos": [
                    {
                        "fieldName": "objectid",
                        "label": "OBJECTID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "id",
                        "label": "ID",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "name",
                        "label": "NAME",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "state_name",
                        "label": "STATE_NAME",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                    },
                    {
                        "fieldName": "area0",
                        "label": "AREA",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 2, "digitSeparator": True},
                    },
                    {
                        "fieldName": "pop2000",
                        "label": "POP2000",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 0, "digitSeparator": True},
                    },
                    {
                        "fieldName": "households",
                        "label": "HOUSEHOLDS",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 0, "digitSeparator": True},
                    },
                    {
                        "fieldName": "hse_units",
                        "label": "HSE_UNITS",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 0, "digitSeparator": True},
                    },
                    {
                        "fieldName": "bus_count",
                        "label": "BUS_COUNT",
                        "isEditable": True,
                        "tooltip": "",
                        "visible": True,
                        "stringFieldOption": "textbox",
                        "format": {"places": 0, "digitSeparator": True},
                    },
                    {
                        "fieldName": "globalid",
                        "label": "GlobalID",
                        "isEditable": False,
                        "tooltip": "",
                        "visible": False,
                        "stringFieldOption": "textbox",
                    },
                ],
                "description": None,
                "showAttachments": True,
                "mediaInfos": [],
            },
        },
    ],
    "baseMap": {
        "baseMapLayers": [
            {
                "id": "defaultBasemap",
                "layerType": "ArcGISTiledMapServiceLayer",
                "url": "https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer",
                "visibility": True,
                "opacity": 1,
                "title": "Topographic",
            }
        ],
        "title": "Topographic",
    },
    "spatialReference": {"wkid": 102100, "latestWkid": 3857},
    "authoringApp": "WebMapViewer",
    "authoringAppVersion": "10.8.1",
    "version": "2.16",
    "applicationProperties": {
        "viewing": {
            "routing": {"enabled": True},
            "basemapGallery": {"enabled": True},
            "measure": {"enabled": True},
        }
    },
}


@integration_test
@profiles.admin_all
class TestFolderAddContent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.small_shp = get_resource_path("staging_data/folders/shapefile.zip", unique_copy=True)
        cls.large_sd = get_web_resource_path("data/servicedefinition.sd", unique_copy=True)

        cls.folder_mgr = cls.gis.content.folders
        cls.root_folder = cls.folder_mgr.get()

        cls.owner = cls.gis.users.create(
            username=f"folder_content_user_{uuid.uuid4().hex[:4]}",
            password="folder_content_user_123",
            firstname="folder",
            lastname="content",
            email="pythonapitest@esri.com",
            role="org_publisher",
        )
        cls.owner.reset(
            password="folder_content_user_123",
            new_password="folder_content_user_1234",
            new_security_question=1,
            new_security_answer="redlands",
            reset_by_email=False,
        )

        cls.items = []
        cls.folders = []

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items(cls.items)
        cls.owner.delete()

    def test_add_by_io(self):
        URL = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/airline-passengers.csv"
        buffer = io.StringIO()
        df = pd.read_csv(URL)
        df.to_csv(buffer)
        item_passengers = self.root_folder.add(
            item_properties=ItemProperties(
                title=f"Airline Passenger IO Data {uuid.uuid4().hex[:4]}",
                item_type=ItemTypeEnum.CSV,
                tags=INTEGRATION_TEST_ITEM_TAG,
                file_name=f"airline_{uuid.uuid4().hex[:5]}.csv"
            ),
            file=buffer,
        ).result()
        assert isinstance(item_passengers, Item)
        assert item_passengers.type == "CSV"
        self.items.append(item_passengers)

    def test_add_service_url(self):
        item = self.root_folder.add(
            item_properties=ItemProperties(
                title=f"url map service {uuid.uuid4().hex[:4]}",
                item_type=ItemTypeEnum.MAP_SERVICE,
                tags=INTEGRATION_TEST_ITEM_TAG,
            ),
            url="https://sampleserver5.arcgisonline.com/arcgis/rest/services/AGP/USA/MapServer",
        ).result()
        assert isinstance(item, Item)
        assert item.type == "Map Service"
        self.items.append(item)

    def test_add_data_url(self):
        item = self.root_folder.add(
            item_properties=ItemProperties(
                title=f"data url shapefile {uuid.uuid4().hex[:4]}",
                item_type=ItemTypeEnum.SHAPEFILE,
                tags=INTEGRATION_TEST_ITEM_TAG,
            ),
            data_url="https://files.hawaii.gov/dbedt/op/gis/data/cah_habitat_status_poly.shp.zip",
        )
        item = item.result()
        assert isinstance(item, Item)
        assert item.type == "Shapefile"
        self.items.append(item)

    def test_add_text(self):
        item = self.root_folder.add(
            item_properties=ItemProperties(
                title=f"text webmap {uuid.uuid4().hex[:4]}",
                item_type=ItemTypeEnum.WEB_MAP,
                tags=INTEGRATION_TEST_ITEM_TAG,
            ),
            text=TEXT_DATA,
        )
        item = item.result()
        assert isinstance(item, Item)
        assert item.type == "Web Map"
        self.items.append(item)

    def test_add_small_file_root(self):
        """adds a small item on the root"""
        item = self.root_folder.add(
            item_properties=ItemProperties(
                title=f"root small file {uuid.uuid4().hex[:4]}",
                item_type=ItemTypeEnum.SHAPEFILE,
                tags=INTEGRATION_TEST_ITEM_TAG,
        ),
            file=self.small_shp,
        )
        item = item.result()
        assert isinstance(item, Item)
        assert item.type == "Shapefile"
        self.items.append(item)

    def test_add_small_file_folder(self):
        """adds a small item inside a folder"""
        unique_folder_name = f"folder_{uuid.uuid4().hex[:4]}"
        folder = self.folder_mgr.create(unique_folder_name)
        item = folder.add(
            item_properties=ItemProperties(
                title=f"folder small file {uuid.uuid4().hex[:4]}",
                item_type=ItemTypeEnum.SHAPEFILE,
                tags=INTEGRATION_TEST_ITEM_TAG,
            ),
            file=self.small_shp,
        )
        item = item.result()
        assert isinstance(item, Item)
        assert folder.delete(permanent=True)

    def test_add_small_file_owner_root(self):
        """adds a small item inside root through owner"""
        owner_root_folder = self.folder_mgr.get(owner=self.owner)
        item = owner_root_folder.add(
            item_properties=ItemProperties(
                title=f"owner root small file {uuid.uuid4().hex[:4]}",
                item_type=ItemTypeEnum.SHAPEFILE,
                tags=INTEGRATION_TEST_ITEM_TAG,
            ),
            file=self.small_shp,
        )
        item = item.result()
        assert isinstance(item, Item)
        self.items.append(item)

    def test_add_small_file_owner_folder(self):
        """adds a small item inside a folder through owner"""
        unique_folder_name = f"folder_{uuid.uuid4().hex[:4]}"
        owner = [user for user in self.gis.users.search("*")][0]
        owner_folder = self.folder_mgr.create(unique_folder_name, owner=self.owner)
        item = owner_folder.add(
            item_properties=ItemProperties(
                title=f"owner small file {uuid.uuid4().hex[:4]}",
                item_type=ItemTypeEnum.SHAPEFILE,
                tags=INTEGRATION_TEST_ITEM_TAG,
            ),
            file=self.small_shp,
        )
        item = item.result()
        assert isinstance(item, Item)
        assert owner_folder.delete(permanent=True)

    def test_add_large_file(self):
        """adds a large item inside a folder"""
        unique_folder_name: str = f"folder_{uuid.uuid4().hex[:4]}"
        folder = self.folder_mgr.create(unique_folder_name)
        item = folder.add(
            item_properties=ItemProperties(
                title=f"sd data {uuid.uuid4().hex[:4]}",
                item_type=ItemTypeEnum.SERVICE_DEFINITION,
                tags=INTEGRATION_TEST_ITEM_TAG,
            ),
            file=self.large_sd,
        )
        item = item.result()
        assert os.stat(self.large_sd).st_size == item.size
        assert isinstance(item, Item)
        assert folder.delete(permanent=True)


@integration_test
@profiles.all
class TestFolder(unittest.TestCase):

    def test_folder_delete_exists_ok(self):
        unique_folder_name = f"folder_{uuid.uuid4().hex[:4]}"
        folder = self.gis.content.folders.create(
            folder=unique_folder_name, exist_ok=True
        )
        assert isinstance(folder, Folder)
        assert folder.delete(permanent=True)

    def test_folder_delete_exists_ok_false_exception(self):
        unique_folder_name = f"folder_{uuid.uuid4().hex[:4]}"
        folder = self.gis.content.folders.create(
            folder=unique_folder_name, exist_ok=True
        )
        with self.assertRaises(FolderException) as context:
            folder = self.gis.content.folders.create(
                folder=unique_folder_name, exist_ok=False
            )
        assert folder.delete(permanent=True)

    def test_folder_delete(self):
        unique_folder_name = f"folder_{uuid.uuid4().hex[:4]}"
        folder = self.gis.content.folders.create(folder=unique_folder_name)
        assert folder.delete(permanent=True)

    def test_folder_properties(self):
        unique_folder_name = f"folder_{uuid.uuid4().hex[:4]}"
        folder = self.gis.content.folders.create(folder=unique_folder_name)
        assert folder.properties
        assert folder.properties['title'] == unique_folder_name
        assert folder.delete(permanent=True)

    def test_folder_name(self):
        unique_folder_name = f"folder_{uuid.uuid4().hex[:4]}"
        folder = self.gis.content.folders.create(folder=unique_folder_name)
        assert folder.name == unique_folder_name
        assert folder.delete(permanent=True)

    def test_folder_list(self):
        folder: Folder = self.gis.content.folders.get("Root Folder")
        for i in folder.list():
            assert isinstance(i, Item)
            break

    def test_folder_rename(self):
        unique_folder_name = f"folder_before_{uuid.uuid4().hex[:4]}"
        unique_folder_name2 = f"folder_after_{uuid.uuid4().hex[:4]}"
        mgr = self.gis.content.folders
        folder = self.gis.content.folders.create(folder=unique_folder_name)
        assert folder.rename(unique_folder_name2)
        assert mgr.get(unique_folder_name2)
        assert mgr.get(unique_folder_name) is None
        assert folder.name == unique_folder_name2
        assert folder.delete(permanent=True)


@integration_test
@profiles.admin_all
class TestFolders(unittest.TestCase):

    def test_property_folders(self):
        assert self.gis.content.folders
        assert isinstance(self.gis.content.folders, Folders)

    def test_create_folder(self):
        folder = self.gis.content.folders.create(folder=f"folder_{uuid.uuid4().hex[:4]}")
        assert isinstance(folder, Folder)
        assert folder.delete(permanent=True)

    def test_create_folder_another_user(self):
        for user in self.gis.users.search("*"):
            if user["username"] != self.gis.users.me.username:
                owner = user["username"]
                break
        folder = self.gis.content.folders.create(folder=f"folder_{uuid.uuid4().hex[:4]}", owner=owner)
        assert isinstance(folder, Folder)
        assert folder.delete(permanent=True)

    def test_get_folder_other_user(self):
        for user in self.gis.users.search("*"):
            if user["username"] != self.gis.users.me.username:
                owner = user["username"]
                break
        mgr: Folders = self.gis.content.folders
        p = [f.name for f in mgr.list(owner=owner)]
        if len(p) > 1:
            folder_name = p[1]
            folder: Folder = mgr.get(folder_name, owner=owner)
            assert folder.name.lower() == folder_name.lower()

    def test_get_folder_self(self):
        mgr: Folders = self.gis.content.folders
        p = [f.name for f in mgr.list()]
        if len(p) > 1:
            folder_name = p[1]
            folder: Folder = mgr.get(folder_name)
            assert folder.name.lower() == folder_name.lower()
            assert folder.properties['username'] == self.gis.users.me.username

    def test_list_folders_current_user(self):
        """lists the folders of the current user"""
        folders: Folders = self.gis.content.folders
        for folder in folders.list():
            assert isinstance(folder, Folder)

    def test_list_folders_different_user(self):
        """lists the folders of the current user"""
        for user in self.gis.users.search("*"):
            if user["username"] != self.gis.users.me.username:
                owner = user["username"]
                break
        folders: Folders = self.gis.content.folders
        for folder in folders.list(owner=owner):
            assert isinstance(folder, Folder)


if __name__ == "__main__":
    unittest.main()
