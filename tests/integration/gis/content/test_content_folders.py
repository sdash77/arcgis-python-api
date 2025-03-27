import sys
import os
import io
import uuid
import unittest
from arcgis.gis import Item
from arcgis.gis._impl._content_manager import Folder, Folders
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging
from integration.config import QALAB_ROOT_PATH
import pandas as pd
from arcgis.gis._impl._content_manager.folder import FolderException

enable_verbose_logging()
QA_LABS_FOLDER = os.path.join(QALAB_ROOT_PATH, "folder_add_content")
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
@profiles.admin_enterprise_and_agol
class TestFolderAddContent(unittest.TestCase):

    def test_add_by_io(self):
        URL = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/airline-passengers.csv"
        buffer = io.StringIO()
        df = pd.read_csv(URL)
        df.to_csv(buffer)
        gis = self.gis
        folders = gis.content.folders
        folder = folders.get("root")

        item_passengers = folder.add(
            item_properties={
                "type": "CSV",
                "title": f"Airline Passenger IO Data {uuid.uuid4().hex[:4]}",
                "fileName": f"airline{uuid.uuid4().hex[:5]}.csv",
                "tags": "integration_testing",
            },
            file=buffer,
        ).result()
        assert isinstance(item_passengers, Item)
        assert item_passengers.type == "CSV"
        assert item_passengers.delete(permanent=True)

    def test_add_service_url(self):
        gis = self.gis
        mgr = gis.content.folders
        folder = mgr.get("Root Folder")
        item = folder.add(
            item_properties={
                "title": f"url map service {uuid.uuid4().hex[:4]}",
                "type": "Map Service",
                "tags": "integration_testing",
            },
            url="https://sampleserver5.arcgisonline.com/arcgis/rest/services/AGP/USA/MapServer",
        )
        item = item.result()
        assert isinstance(item, Item)
        assert item.type == "Map Service"
        assert item.delete(permanent=True)

    def test_add_data_url(self):
        gis = self.gis
        mgr = gis.content.folders
        folder = mgr.get("Root Folder")
        item = folder.add(
            item_properties={
                "title": f"data url shapefile {uuid.uuid4().hex[:4]}",
                "type": "Shapefile",
                "tags": "integration_testing",
            },
            data_url="https://www2.census.gov/geo/tiger/TIGER2022/STATE/tl_2022_us_state.zip",
        )
        item = item.result()
        assert isinstance(item, Item)
        assert item.type == "Shapefile"
        assert item.delete(permanent=True)

    def test_add_text(self):
        gis = self.gis
        mgr = gis.content.folders
        folder = mgr.get("Root Folder")
        item = folder.add(
            item_properties={
                "title": f"text webmap {uuid.uuid4().hex[:4]}",
                "type": "Web Map",
                "tags": "integration_testing",
            },
            text=TEXT_DATA,
        )
        item = item.result()
        assert isinstance(item, Item)
        assert item.type == "Web Map"
        assert item.delete(permanent=True)

    def test_add_small_file_root(self):
        """adds a small item on the root"""
        gis = self.gis
        mgr = gis.content.folders
        folder = mgr.get("Root Folder")
        item = folder.add(
            item_properties={
                "title": f"root small file {uuid.uuid4().hex[:4]}",
                "type": "Shapefile",
                "tags": "integration_testing",
            },
            file=os.path.join(QA_LABS_FOLDER, "shapefile.zip"),
        )
        item = item.result()
        assert isinstance(item, Item)
        assert item.type == "Shapefile"
        assert item.delete(permanent=True)

    def test_add_small_file_folder(self):
        """adds a small item inside a folder"""
        gis = self.gis
        unique_folder_name: str = "integration_testing_folder_add_small_file"
        mgr = gis.content.folders
        folder = mgr.create(unique_folder_name)

        item = folder.add(
            item_properties={
                "title": f"folder small file {uuid.uuid4().hex[:4]}",
                "type": "Shapefile",
                "tags": "integration_testing",
            },
            file=os.path.join(QA_LABS_FOLDER, "shapefile.zip"),
        )
        item = item.result()
        assert isinstance(item, Item)
        assert item.delete(permanent=True)
        assert folder.delete(permanent=True)

    def test_add_small_file_owner(self):
        """adds a small item inside root through owner"""
        gis = self.gis
        mgr = gis.content.folders
        owner = [user for user in gis.users.search("*")][0]
        folder = mgr.get("Root Folder", owner=owner)
        item = folder.add(
            item_properties={
                "title": f"owner small file {uuid.uuid4().hex[:4]}",
                "type": "Shapefile",
                "tags": "integration_testing",
            },
            file=os.path.join(QA_LABS_FOLDER, "shapefile.zip"),
            # owner=owner,
        )
        item = item.result()
        assert isinstance(item, Item)
        assert item.delete(permanent=True)

    def test_add_small_file_folder_owner(self):
        """"""
        gis = self.gis
        unique_folder_name: str = (
            "integration_testing_folder_add_small_file_owner"
        )
        mgr = gis.content.folders
        owner = [user for user in gis.users.search("*")][0]
        folder = mgr.create(unique_folder_name)

        item = folder.add(
            item_properties={
                "title": "shapefile_data",
                "type": "Shapefile",
                "tags": "integration_testing",
            },
            file=os.path.join(QA_LABS_FOLDER, "shapefile.zip"),
            # owner=owner,
        )
        item = item.result()
        assert isinstance(item, Item)
        assert item.delete(permanent=True)
        assert folder.delete(permanent=True)

    def test_add_large_file(self):
        """adds a large item inside a folder"""
        gis = self.gis
        unique_folder_name: str = "integration_testing_folder_add_large_file"
        mgr = gis.content.folders
        # owner = [user for user in gis.users.search("*")][0]
        folder = mgr.create(unique_folder_name)

        item = folder.add(
            item_properties={
                "title": "sd_data",
                "type": "Service Definition",
                "tags": "integration_testing",
            },
            file=os.path.join(QA_LABS_FOLDER, "servicedefinition.sd"),
        )
        item = item.result()
        assert (
            os.stat(
                os.path.join(QA_LABS_FOLDER, "servicedefinition.sd")
            ).st_size
            == item.size
        )
        assert isinstance(item, Item)
        assert item.delete(permanent=True)
        assert folder.delete(permanent=True)


@integration_test
@profiles.enterprise_and_agol
class TestFolder(unittest.TestCase):

    def test_folder_delete_exists_ok(self):
        unique_folder_name: str = "integration_exists_ok_true"
        gis = self.gis
        folder = gis.content.folders.create(
            folder=unique_folder_name, exist_ok=True
        )
        assert isinstance(folder, Folder)
        assert folder.delete(permanent=True)

    def test_folder_delete_exists_ok_false(self):
        unique_folder_name: str = "integration_exists_ok_false"
        gis = self.gis
        folder = gis.content.folders.create(
            folder=unique_folder_name, exist_ok=True
        )
        with self.assertRaises(FolderException) as context:
            folder = gis.content.folders.create(
                folder=unique_folder_name, exists_ok=False
            )
        assert folder.delete(permanent=True)

    def test_folder_delete(self):
        unique_folder_name: str = "integration_testing_folder_delete"
        gis = self.gis
        folder = gis.content.folders.create(folder=unique_folder_name)
        assert folder.delete(permanent=True)

    def test_folder_properties(self):
        unique_folder_name: str = "integration_testing_folder_properties"
        gis = self.gis
        folder = gis.content.folders.create(folder=unique_folder_name)
        assert folder.properties
        assert folder.delete(permanent=True)

    def test_folder_name(self):
        unique_folder_name: str = "integration_testing_folder_name"
        gis = self.gis
        folder = gis.content.folders.create(folder=unique_folder_name)
        assert folder.name
        assert folder.delete(permanent=True)

    def test_folder_list(self):
        gis = self.gis
        folder: Folder = gis.content.folders.get("Root Folder")
        for i in folder.list():
            assert isinstance(i, Item)
            break

    def test_folder_rename(self):
        unique_folder_name: str = "integration_testing_folder_before"
        unique_folder_name2: str = "integration_testing_folder_after"
        gis = self.gis
        mgr = gis.content.folders
        folder = gis.content.folders.create(folder=unique_folder_name)
        assert folder.rename(unique_folder_name2)
        assert mgr.get(unique_folder_name2)
        assert mgr.get(unique_folder_name) is None
        assert folder.name == unique_folder_name2
        assert folder.delete(permanent=True)


@integration_test
@profiles.admin_enterprise_and_agol
class TestFolders(unittest.TestCase):

    def test_property_folders(self):
        gis = self.gis
        assert gis.content.folders
        assert isinstance(gis.content.folders, Folders)

    def test_create_folder(self):
        gis = self.gis
        folder = gis.content.folders.create(
            folder="integration_testing_folders_create"
        )
        assert isinstance(folder, Folder)
        assert folder.delete(permanent=True)

    def test_create_folder_another_user(self):
        gis = self.gis
        owner: str = None
        for user in gis.users.search("*"):
            if user["username"] != gis.users.me.username:
                owner = user["username"]
                break
        folder = gis.content.folders.create(
            folder="integration_testing_folder_create_for_owner", owner=owner
        )
        assert isinstance(folder, Folder)
        assert folder.delete(permanent=True)

    def test_get_folder_other_user(self):
        gis = self.gis
        if gis.users.me:
            for user in gis.users.search("*"):
                if user["username"] != gis.users.me.username:
                    owner = user["username"]
                    break
            mgr: Folders = gis.content.folders
            p = [f for f in mgr.list(owner=owner)]
            p = [f.name for f in mgr.list(owner=owner)]
            for f in mgr.list(owner=owner):
                f.name
            if len(p) > 1:
                folder_name = p[1]
                folder: Folder = mgr.get(folder_name, owner=owner)
                assert folder.name.lower() == folder_name.lower()

    def test_get_folder_self(self):
        gis = self.gis
        mgr: Folders = gis.content.folders
        p = [f.name for f in mgr.list()]
        if len(p) > 1:
            folder_name = p[1]
            folder: Folder = mgr.get(folder_name)
            assert folder.name.lower() == folder_name.lower()

    def test_list_folders_current_user(self):
        """lists the folders of the current user"""
        gis = self.gis
        folders: Folders = gis.content.folders
        for folder in folders.list():
            assert isinstance(folder, Folder)

    def test_list_folders_different_user(self):
        """lists the folders of the current user"""
        gis = self.gis
        if gis.users.me:
            for user in gis.users.search("*"):
                if user["username"] != gis.users.me.username:
                    owner = user["username"]
                    break
            folders: Folders = gis.content.folders
            for folder in folders.list(owner=owner):
                assert isinstance(folder, Folder)


if __name__ == "__main__":
    unittest.main()
