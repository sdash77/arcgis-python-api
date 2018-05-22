tool_xml_file_name = r"{toolbox}.{tool}.pyt.xml"

parameter_template = r'<param name="{name}" displayname="{name}" type="{inputtype}" direction="{direction}" datatype="{dtype}" expression="{name}"><dialogReference>&lt;DIV STYLE="text-align:Left;"&gt;&lt;DIV&gt;&lt;P&gt;&lt;SPAN&gt;{description}&lt;/SPAN&gt;&lt;/P&gt;&lt;/DIV&gt;&lt;/DIV&gt;</dialogReference></param>'

toolxmltemplate = r'''<?xml version="1.0"?>
<metadata xml:lang="en">
	<Esri>
		<CreaDate>{date}</CreaDate>
		<CreaTime>{ctime}</CreaTime>
		<ArcGISFormat>1.0</ArcGISFormat>
		<SyncOnce>TRUE</SyncOnce>
		<ModDate>{date}</ModDate>
		<ModTime>{ctime}</ModTime>
		<scaleRange>
			<minScale>150000000</minScale>
			<maxScale>5000</maxScale>
		</scaleRange>
	</Esri>
	<tool name="{name}" displayname="{name}" toolboxalias=""
		xmlns="">
		<arcToolboxHelpPath>c:\program files\arcgis\pro\Resources\Help\gp</arcToolboxHelpPath>
		<parameters>
			{parameters}
		</parameters>
		<summary>&lt;DIV STYLE="text-align:Left;"&gt;&lt;DIV&gt;&lt;P&gt;&lt;SPAN&gt;{summary}&lt;/SPAN&gt;&lt;/P&gt;&lt;P&gt;&lt;SPAN /&gt;&lt;/P&gt;&lt;P STYLE="text-indent:20;"&gt;&lt;SPAN /&gt;&lt;/P&gt;&lt;/DIV&gt;&lt;/DIV&gt;</summary>
		<usage>&lt;DIV STYLE="text-align:Left;"&gt;&lt;DIV&gt;&lt;P&gt;&lt;SPAN&gt;{usage}&lt;/SPAN&gt;&lt;/P&gt;&lt;/DIV&gt;&lt;/DIV&gt;</usage>
	</tool>
	<dataIdInfo>
		<idCitation>
			<resTitle>{name}</resTitle>
		</idCitation>
		<searchKeys>
			<keyword>{tag}</keyword>
		</searchKeys>
	</dataIdInfo>
	<distInfo>
		<distributor>
			<distorFormat>
				<formatName>ArcToolbox Tool</formatName>
			</distorFormat>
		</distributor>
	</distInfo>
	<mdHrLv>
		<ScopeCd value="005"></ScopeCd>
	</mdHrLv>
	<mdDateSt Sync="TRUE">{date}</mdDateSt>
</metadata>'''

xmltemplate = r'''<?xml version="1.0" encoding="UTF-8"?>
<metadata xml:lang="en"><Esri><CreaDate>20180419</CreaDate><CreaTime>12251200</CreaTime><ArcGISFormat>1.0</ArcGISFormat><SyncOnce>TRUE</SyncOnce><ModDate>20180419</ModDate><ModTime>122512</ModTime></Esri><toolbox name="{toolbox}" alias=""><arcToolboxHelpPath>c:\program files\arcgis\pro\Resources\Help\gp</arcToolboxHelpPath><toolsets/></toolbox><dataIdInfo><idCitation><resTitle>{toolbox}</resTitle></idCitation></dataIdInfo><distInfo><distributor><distorFormat><formatName>ArcToolbox Toolbox</formatName></distorFormat></distributor></distInfo></metadata>'''

pyttemplate = r'''
"""
@author:
@contact:
@version:
@description:
@requirements:
@copyright:
"""
from arcgis.features import SpatialDataFrame, FeatureLayer #
from arcgis.features.layer import FeatureLayerCollection #
from arcgis.geocoding import Geocoder
from arcgis.geoprocessing._tool import Toolbox #

from arcgis.network import NetworkDataset #
from arcgis.gis import Layer
from arcgis.mapping import VectorTileLayer
from arcgis.mapping import MapImageLayer #
from arcgis.raster import ImageryLayer
from arcgis.schematics import SchematicLayers
from arcgis.mapping._types import SceneLayer

import pandas
import pandas as pd
import numpy
import numpy as np

import os
import sys
import traceback

import arcpy
from arcpy import env
from arcpy import da

if sys.version_info.major == 3:
    from arcpy import mp as mapping
else:
    from arcpy import mapping

env.overwriteOutput = True

#--------------------------------------------------------------------------
class FunctionError(Exception):
    """ raised when a function fails to run """
    pass

#--------------------------------------------------------------------------
def trace():
    """
        trace finds the line, the filename
        and error message and returns it
        to the user
    """
    import traceback
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    # script name + line number
    line = tbinfo.split(", ")[1]
    # Get Python syntax error
    #
    synerror = traceback.format_exc().splitlines()[-1]
    return line, __file__, synerror

{imports}
{code}

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "{toolbox}"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [{tool}]


class {tool}(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "{tool}"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
{parameters}
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        try:
{use}

        except arcpy.ExecuteError:
            line, filename, synerror = trace()
            arcpy.AddError("error on line: %s" % line)
            arcpy.AddError("error in file name: %s" % filename)
            arcpy.AddError("with error message: %s" % synerror)
            arcpy.AddError("ArcPy Error Message: %s" % arcpy.GetMessages(2))
        except FunctionError as f_e:
            messages = f_e.args[0]
            arcpy.AddError("error in function: %s" % messages["function"])
            arcpy.AddError("error on line: %s" % messages["line"])
            arcpy.AddError("error in file name: %s" % messages["filename"])
            arcpy.AddError("with error message: %s" % messages["synerror"])
            arcpy.AddError("ArcPy Error Message: %s" % messages["arc"])
        except:
            line, filename, synerror = trace()
            arcpy.AddError("error on line: %s" % line)
            arcpy.AddError("error in file name: %s" % filename)
            arcpy.AddError("with error message: %s" % synerror)
        return
'''