import sys

#
#  Update the Path to set the test area
sys.path.insert(0, r"C:\SVN\geosaurus_master\src")
import os
import uuid
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS, Item
from arcgis.gis._impl._content_manager import Folder, Folders

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ['your_online_profile', 'your_enterprise_profile']
QA_LABS_FOLDER = r"\\qalab_server\pydata\v109\geosaurus\folder_add_content"
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)
TEXT_DATA = {
    'operationalLayers': [
        {
            'id': 'CA_Fire_Boundaries_9995',
            'layerType': 'ArcGISMapServiceLayer',
            'url': 'https://pythonapi.playground.esri.com/server/rest/services/CA_Fire_Boundaries/MapServer',
            'visibility': True,
            'opacity': 1,
            'title': 'CA_Fire_Boundaries',
            'itemId': '3f736ece6c154aabaf8420247adbdecd',
        },
        {
            'id': 'SanFranciscoDataLayers_4326_2624',
            'layerType': 'ArcGISFeatureLayer',
            'url': 'https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/12',
            'visibility': True,
            'opacity': 1,
            'mode': 1,
            'title': 'SanFranciscoDataLayers_4326 - Parks',
            'itemId': 'a144dd9463454fe99cbdedc86d6495ae',
            'popupInfo': {
                'title': 'Parks: {name}',
                'fieldInfos': [
                    {
                        'fieldName': 'objectid',
                        'label': 'OBJECTID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'id',
                        'label': 'ID',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'featarea',
                        'label': 'FEATAREA',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'featperim',
                        'label': 'FEATPERIM',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'name',
                        'label': 'NAME',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'displtyp',
                        'label': 'DISPLTYP',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 0, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'globalid',
                        'label': 'GlobalID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'SHAPE__Length',
                        'label': 'SHAPE__Length',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'SHAPE__Area',
                        'label': 'SHAPE__Area',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                ],
                'description': None,
                'showAttachments': True,
                'mediaInfos': [],
            },
        },
        {
            'id': 'SanFranciscoDataLayers_4326_5308',
            'layerType': 'ArcGISFeatureLayer',
            'url': 'https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/11',
            'visibility': True,
            'opacity': 1,
            'mode': 1,
            'title': 'SanFranciscoDataLayers_4326 - Landmarks',
            'itemId': 'a144dd9463454fe99cbdedc86d6495ae',
            'popupInfo': {
                'title': 'Landmarks: {name}',
                'fieldInfos': [
                    {
                        'fieldName': 'objectid',
                        'label': 'OBJECTID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'name',
                        'label': 'NAME',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'fcc',
                        'label': 'FCC',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'globalid',
                        'label': 'GlobalID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'SHAPE__Length',
                        'label': 'SHAPE__Length',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'SHAPE__Area',
                        'label': 'SHAPE__Area',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                ],
                'description': None,
                'showAttachments': True,
                'mediaInfos': [],
            },
        },
        {
            'id': 'SanFranciscoDataLayers_4326_3522',
            'layerType': 'ArcGISFeatureLayer',
            'url': 'https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/10',
            'visibility': True,
            'opacity': 1,
            'mode': 1,
            'title': 'SanFranciscoDataLayers_4326 - Highways',
            'itemId': 'a144dd9463454fe99cbdedc86d6495ae',
            'popupInfo': {
                'title': 'Highways: {name}',
                'fieldInfos': [
                    {
                        'fieldName': 'objectid',
                        'label': 'OBJECTID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'prefix',
                        'label': 'PREFIX',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'pretype',
                        'label': 'PRETYPE',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'name',
                        'label': 'NAME',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'type',
                        'label': 'TYPE',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'suffix',
                        'label': 'SUFFIX',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'fcc',
                        'label': 'FCC',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'acc',
                        'label': 'ACC',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'shield',
                        'label': 'SHIELD',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'hwy_num',
                        'label': 'HWY_NUM',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'globalid',
                        'label': 'GlobalID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'SHAPE__Length',
                        'label': 'SHAPE__Length',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                ],
                'description': None,
                'showAttachments': True,
                'mediaInfos': [],
            },
        },
        {
            'id': 'SanFranciscoDataLayers_4326_2877',
            'layerType': 'ArcGISFeatureLayer',
            'url': 'https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/9',
            'visibility': True,
            'opacity': 1,
            'mode': 1,
            'title': 'SanFranciscoDataLayers_4326 - Rivers',
            'itemId': 'a144dd9463454fe99cbdedc86d6495ae',
            'popupInfo': {
                'title': 'Rivers: {name}',
                'fieldInfos': [
                    {
                        'fieldName': 'objectid',
                        'label': 'OBJECTID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'name',
                        'label': 'NAME',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'fcc',
                        'label': 'FCC',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'globalid',
                        'label': 'GlobalID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'SHAPE__Length',
                        'label': 'SHAPE__Length',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                ],
                'description': None,
                'showAttachments': True,
                'mediaInfos': [],
            },
        },
        {
            'id': 'SanFranciscoDataLayers_4326_4178',
            'layerType': 'ArcGISFeatureLayer',
            'url': 'https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/8',
            'visibility': True,
            'opacity': 1,
            'mode': 1,
            'title': 'SanFranciscoDataLayers_4326 - sf_stores',
            'itemId': 'a144dd9463454fe99cbdedc86d6495ae',
            'popupInfo': {
                'title': 'sf_stores: {store_id}',
                'fieldInfos': [
                    {
                        'fieldName': 'objectid',
                        'label': 'FID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'store_id',
                        'label': 'STORE_ID',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'globalid',
                        'label': 'GlobalID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                ],
                'description': None,
                'showAttachments': True,
                'mediaInfos': [],
            },
        },
        {
            'id': 'SanFranciscoDataLayers_4326_9036',
            'layerType': 'ArcGISFeatureLayer',
            'url': 'https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/7',
            'visibility': True,
            'opacity': 1,
            'mode': 1,
            'title': 'SanFranciscoDataLayers_4326 - sf_cust',
            'itemId': 'a144dd9463454fe99cbdedc86d6495ae',
            'popupInfo': {
                'title': 'sf_cust: {store_id}',
                'fieldInfos': [
                    {
                        'fieldName': 'objectid',
                        'label': 'FID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'store_id',
                        'label': 'STORE_ID',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'globalid',
                        'label': 'GlobalID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                ],
                'description': None,
                'showAttachments': True,
                'mediaInfos': [],
            },
        },
        {
            'id': 'SanFranciscoDataLayers_4326_2413',
            'layerType': 'ArcGISFeatureLayer',
            'url': 'https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/6',
            'visibility': True,
            'opacity': 1,
            'mode': 1,
            'title': 'SanFranciscoDataLayers_4326 - End Locations',
            'itemId': 'a144dd9463454fe99cbdedc86d6495ae',
            'popupInfo': {
                'title': 'End Locations: {status}',
                'fieldInfos': [
                    {
                        'fieldName': 'objectid',
                        'label': 'OBJECTID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'routeid',
                        'label': 'RouteID',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 0, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'start_x',
                        'label': 'Start_X',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'start_y',
                        'label': 'Start_Y',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'end_x',
                        'label': 'End_X',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'end_y',
                        'label': 'End_Y',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'status',
                        'label': 'Expected Status',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'globalid',
                        'label': 'GlobalID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                ],
                'description': None,
                'showAttachments': True,
                'mediaInfos': [],
            },
        },
        {
            'id': 'SanFranciscoDataLayers_4326_2775',
            'layerType': 'ArcGISFeatureLayer',
            'url': 'https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/5',
            'visibility': True,
            'opacity': 1,
            'mode': 1,
            'title': 'SanFranciscoDataLayers_4326 - Start Locations',
            'itemId': 'a144dd9463454fe99cbdedc86d6495ae',
            'popupInfo': {
                'title': 'Start Locations: {status}',
                'fieldInfos': [
                    {
                        'fieldName': 'objectid',
                        'label': 'OBJECTID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'routeid',
                        'label': 'RouteID',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 0, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'start_x',
                        'label': 'Start_X',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'start_y',
                        'label': 'Start_Y',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'end_x',
                        'label': 'End_X',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'end_y',
                        'label': 'End_Y',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'status',
                        'label': 'Expected Status',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'globalid',
                        'label': 'GlobalID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                ],
                'description': None,
                'showAttachments': True,
                'mediaInfos': [],
            },
        },
        {
            'id': 'SanFranciscoDataLayers_4326_2872',
            'layerType': 'ArcGISFeatureLayer',
            'url': 'https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/4',
            'visibility': True,
            'opacity': 1,
            'mode': 1,
            'title': 'SanFranciscoDataLayers_4326 - Stores',
            'itemId': 'a144dd9463454fe99cbdedc86d6495ae',
            'popupInfo': {
                'title': 'Stores: {name}',
                'fieldInfos': [
                    {
                        'fieldName': 'objectid',
                        'label': 'OBJECTID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'name',
                        'label': 'NAME',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'demand',
                        'label': 'Demand',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'servicetime',
                        'label': 'ServiceTime',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'timestart1',
                        'label': 'TimeStart1',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'dateFormat': 'shortDateShortTime'},
                    },
                    {
                        'fieldName': 'timeend1',
                        'label': 'TimeEnd1',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'dateFormat': 'shortDateShortTime'},
                    },
                    {
                        'fieldName': 'globalid',
                        'label': 'GlobalID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                ],
                'description': None,
                'showAttachments': True,
                'mediaInfos': [],
            },
        },
        {
            'id': 'SanFranciscoDataLayers_4326_2726',
            'layerType': 'ArcGISFeatureLayer',
            'url': 'https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/3',
            'visibility': True,
            'opacity': 1,
            'mode': 1,
            'title': 'SanFranciscoDataLayers_4326 - Distribution Center',
            'itemId': 'a144dd9463454fe99cbdedc86d6495ae',
            'popupInfo': {
                'title': 'Distribution Center: {name}',
                'fieldInfos': [
                    {
                        'fieldName': 'objectid',
                        'label': 'OBJECTID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'name',
                        'label': 'NAME',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'globalid',
                        'label': 'GlobalID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                ],
                'description': None,
                'showAttachments': True,
                'mediaInfos': [],
            },
        },
        {
            'id': 'SanFranciscoDataLayers_4326_9300',
            'layerType': 'ArcGISFeatureLayer',
            'url': 'https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/2',
            'visibility': True,
            'opacity': 1,
            'mode': 1,
            'title': 'SanFranciscoDataLayers_4326 - Fire Stations',
            'itemId': 'a144dd9463454fe99cbdedc86d6495ae',
            'popupInfo': {
                'title': 'Fire Stations: {name}',
                'fieldInfos': [
                    {
                        'fieldName': 'objectid',
                        'label': 'OBJECTID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'status',
                        'label': 'Status',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'score',
                        'label': 'Score',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 0, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'match_type',
                        'label': 'Match_type',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'side',
                        'label': 'Side',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'match_addr',
                        'label': 'Match_addr',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'name',
                        'label': 'NAME',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'address',
                        'label': 'ADDRESS',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'globalid',
                        'label': 'GlobalID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                ],
                'description': None,
                'showAttachments': True,
                'mediaInfos': [],
            },
        },
        {
            'id': 'SanFranciscoDataLayers_4326_1710',
            'layerType': 'ArcGISFeatureLayer',
            'url': 'https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/1',
            'visibility': True,
            'opacity': 1,
            'mode': 1,
            'title': 'SanFranciscoDataLayers_4326 - Hospitals',
            'itemId': 'a144dd9463454fe99cbdedc86d6495ae',
            'popupInfo': {
                'title': 'Hospitals: {name}',
                'fieldInfos': [
                    {
                        'fieldName': 'objectid',
                        'label': 'OBJECTID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'name',
                        'label': 'NAME',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'fcc',
                        'label': 'FCC',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'globalid',
                        'label': 'GlobalID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                ],
                'description': None,
                'showAttachments': True,
                'mediaInfos': [],
            },
        },
        {
            'id': 'SanFranciscoDataLayers_4326_7720',
            'layerType': 'ArcGISFeatureLayer',
            'url': 'https://pythonapi.playground.esri.com/server/rest/services/Hosted/SanFranciscoDataLayers_4326/FeatureServer/0',
            'visibility': True,
            'opacity': 1,
            'mode': 1,
            'title': 'SanFranciscoDataLayers_4326 - Tract Centroids',
            'itemId': 'a144dd9463454fe99cbdedc86d6495ae',
            'popupInfo': {
                'title': 'Tract Centroids: {name}',
                'fieldInfos': [
                    {
                        'fieldName': 'objectid',
                        'label': 'OBJECTID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'id',
                        'label': 'ID',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'name',
                        'label': 'NAME',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'state_name',
                        'label': 'STATE_NAME',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                    },
                    {
                        'fieldName': 'area0',
                        'label': 'AREA',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 2, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'pop2000',
                        'label': 'POP2000',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 0, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'households',
                        'label': 'HOUSEHOLDS',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 0, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'hse_units',
                        'label': 'HSE_UNITS',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 0, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'bus_count',
                        'label': 'BUS_COUNT',
                        'isEditable': True,
                        'tooltip': '',
                        'visible': True,
                        'stringFieldOption': 'textbox',
                        'format': {'places': 0, 'digitSeparator': True},
                    },
                    {
                        'fieldName': 'globalid',
                        'label': 'GlobalID',
                        'isEditable': False,
                        'tooltip': '',
                        'visible': False,
                        'stringFieldOption': 'textbox',
                    },
                ],
                'description': None,
                'showAttachments': True,
                'mediaInfos': [],
            },
        },
    ],
    'baseMap': {
        'baseMapLayers': [
            {
                'id': 'defaultBasemap',
                'layerType': 'ArcGISTiledMapServiceLayer',
                'url': 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer',
                'visibility': True,
                'opacity': 1,
                'title': 'Topographic',
            }
        ],
        'title': 'Topographic',
    },
    'spatialReference': {'wkid': 102100, 'latestWkid': 3857},
    'authoringApp': 'WebMapViewer',
    'authoringAppVersion': '10.8.1',
    'version': '2.16',
    'applicationProperties': {
        'viewing': {
            'routing': {'enabled': True},
            'basemapGallery': {'enabled': True},
            'measure': {'enabled': True},
        }
    },
}


###########################################################################


class TestFolderAddContent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis_objs = [
            GIS(
                profile='your_enterprise_profile',
                verify_cert=False,
                proxy=PROXIES,
            ),
            GIS(
                profile='your_online_profile',
                verify_cert=False,
                proxy=PROXIES,
            ),
        ]

    def test_add_service_url(self):
        for gis in self.gis_objs:
            mgr = gis.content.folders
            folder = mgr.get("Root Folder")
            item = folder.add(
                item_properties={
                    "title": "url by referrence",
                    "type": 'Map Service',
                },
                url="https://sampleserver5.arcgisonline.com/arcgis/rest/services/AGP/USA/MapServer",
            )
            item = item.result()
            assert isinstance(item, Item)
            assert item.delete()

    def test_add_data_url(self):
        for gis in self.gis_objs:
            mgr = gis.content.folders
            folder = mgr.get("Root Folder")
            item = folder.add(
                item_properties={
                    "title": "data_url_shapefile",
                    "type": 'Shapefile',
                },
                data_url="https://www2.census.gov/geo/tiger/TIGER2022/STATE/tl_2022_us_state.zip",
            )
            item = item.result()
            assert isinstance(item, Item)
            assert item.delete()

    def test_add_text(self):
        for gis in self.gis_objs:
            mgr = gis.content.folders
            folder = mgr.get("Root Folder")
            item = folder.add(
                item_properties={
                    "title": "webmap test",
                    "type": 'Web Map',
                },
                text=TEXT_DATA,
            )
            item = item.result()
            assert isinstance(item, Item)
            assert item.delete()

    def test_add_small_file(self):
        """adds a small item on the root"""
        for gis in self.gis_objs:
            mgr = gis.content.folders
            folder = mgr.get("Root Folder")
            item = folder.add(
                item_properties={
                    "title": "shapefile_data",
                    "type": "Shapefile",
                },
                file=os.path.join(QA_LABS_FOLDER, "shapefile.zip"),
            )
            item = item.result()
            assert isinstance(item, Item)
            item.delete()

    def test_add_small_file_folder(self):
        """adds a small item inside a folder"""

        for gis in self.gis_objs:
            unique_folder_name: str = f"folder_{uuid.uuid4().hex[:4]}"
            mgr = gis.content.folders
            folder = mgr.create(unique_folder_name)

            item = folder.add(
                item_properties={
                    "title": "shapefile_data",
                    "type": "Shapefile",
                },
                file=os.path.join(QA_LABS_FOLDER, "shapefile.zip"),
            )
            item = item.result()
            assert isinstance(item, Item)
            assert item.delete()
            assert folder.delete()

    def test_add_small_file_owner(self):
        """"""

        for gis in self.gis_objs:
            mgr = gis.content.folders
            owner = [user for user in gis.users.search("*")][0]
            folder = mgr.get("Root Folder", owner=owner)
            item = folder.add(
                item_properties={
                    "title": "shapefile_data",
                    "type": "Shapefile",
                },
                file=os.path.join(QA_LABS_FOLDER, "shapefile.zip"),
                # owner=owner,
            )
            item = item.result()
            assert isinstance(item, Item)
            item.delete()

    def test_add_small_file_folder_owner(self):
        """"""
        for gis in self.gis_objs:
            unique_folder_name: str = f"folder_{uuid.uuid4().hex[:4]}"
            mgr = gis.content.folders
            owner = [user for user in gis.users.search("*")][0]
            folder = mgr.create(unique_folder_name)

            item = folder.add(
                item_properties={
                    "title": "shapefile_data",
                    "type": "Shapefile",
                },
                file=os.path.join(QA_LABS_FOLDER, "shapefile.zip"),
                # owner=owner,
            )
            item = item.result()
            assert isinstance(item, Item)
            item.delete()

    def test_add_large_file(self):
        """"""
        for gis in self.gis_objs:
            unique_folder_name: str = f"folder_{uuid.uuid4().hex[:4]}"
            mgr = gis.content.folders
            # owner = [user for user in gis.users.search("*")][0]
            folder = mgr.create(unique_folder_name)

            item = folder.add(
                item_properties={
                    "title": "sd_data",
                    "type": "Service Definition",
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
            item.delete()


###########################################################################


class TestFolder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis_objs = [
            GIS(
                profile='your_enterprise_profile',
                verify_cert=False,
                proxy=PROXIES,
            ),
            GIS(
                profile='your_online_profile',
                verify_cert=False,
                proxy=PROXIES,
            ),
        ]

    def test_folder_delete(self):
        unique_folder_name: str = f"folder_{uuid.uuid4().hex[:4]}"
        for gis in self.gis_objs:
            folder = gis.content.folders.create(folder=unique_folder_name)
            assert folder.delete()

    def test_folder_properties(self):
        unique_folder_name: str = f"folder_{uuid.uuid4().hex[:4]}"
        for gis in self.gis_objs:
            folder = gis.content.folders.create(folder=unique_folder_name)
            assert folder.properties
            assert folder.delete()

    def test_folder_name(self):
        unique_folder_name: str = f"folder_{uuid.uuid4().hex[:4]}"
        for gis in self.gis_objs:
            folder = gis.content.folders.create(folder=unique_folder_name)
            assert folder.name
            assert folder.delete()

    def test_folder_list(self):
        for gis in self.gis_objs:
            folder: Folder = gis.content.folders.get("Root Folder")
            for i in folder.list():
                assert isinstance(i, Item)
                break

    def test_folder_rename(self):
        unique_folder_name: str = f"folder_{uuid.uuid4().hex[:4]}"
        unique_folder_name2: str = f"folder_{uuid.uuid4().hex[:4]}"
        for gis in self.gis_objs:
            mgr = gis.content.folders
            folder = gis.content.folders.create(folder=unique_folder_name)
            assert folder.rename(unique_folder_name2)
            assert mgr.get(unique_folder_name2)
            assert mgr.get(unique_folder_name) is None
            assert folder.name == unique_folder_name2
            assert folder.delete()


###########################################################################


class TestFolders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis_objs = [
            GIS(
                profile='your_enterprise_profile',
                verify_cert=False,
                proxy=PROXIES,
            ),
            GIS(
                profile='your_online_profile',
                verify_cert=False,
                proxy=PROXIES,
            ),
            GIS(verify_cert=False, proxy=PROXIES),
        ]

    def test_property_folders(self):
        for gis in self.gis_objs:
            assert gis.content.folders
            assert isinstance(gis.content.folders, Folders)

    def test_create_folder(self):
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            folder = gis.content.folders.create(
                folder="a folder for testing"
            )
            assert isinstance(folder, Folder)
            assert folder.delete()

    def test_create_folder_another_user(self):
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            owner: str = None
            for user in gis.users.search("*"):
                if user['username'] != gis.users.me.username:
                    owner = user['username']
                    break
            folder = gis.content.folders.create(
                folder="a folder for testing", owner=owner
            )
            assert isinstance(folder, Folder)
            assert folder.delete()

    def test_get_folder_other_user(self):
        for gis in self.gis_objs[:2]:
            for gis in self.gis_objs:
                if gis.users.me:
                    for user in gis.users.search("*"):
                        if user['username'] != gis.users.me.username:
                            owner = user['username']
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
                        break

    def test_get_folder_self(self):
        for gis in self.gis_objs[:2]:
            mgr: Folders = gis.content.folders
            p = [f.name for f in mgr.list()]
            if len(p) > 1:
                folder_name = p[1]
                folder: Folder = mgr.get(folder_name)
                assert folder.name.lower() == folder_name.lower()
                break

    def test_list_folders_current_user(self):
        """lists the folders of the current user"""
        for gis in self.gis_objs:
            folders: Folders = gis.content.folders
            for folder in folders.list():
                assert isinstance(folder, Folder)

    def test_list_folders_different_user(self):
        """lists the folders of the current user"""

        for gis in self.gis_objs:
            if gis.users.me:
                for user in gis.users.search("*"):
                    if user['username'] != gis.users.me.username:
                        owner = user['username']
                        break
                folders: Folders = gis.content.folders
                for folder in folders.list(owner=owner):
                    assert isinstance(folder, Folder)


if __name__ == "__main__":
    unittest.main()
